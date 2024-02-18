import dataclasses
import json
import os
from typing import List, Optional, Tuple

from autogen import ConversableAgent
from typing_extensions import Self

from orchestration.data import ChatMessage, ConversationResult


class Orchestrator:
    """Orchestrators manage conversations between multi-agent teams."""

    def __init__(
        self,
        name: str,
        agents: List[ConversableAgent],
        validate_results_func: Optional[callable] = None,  # type: ignore
        log_dir: str = "logs",
    ):
        if len(agents) < 2:
            raise ValueError("Orchestrator needs at least two agents")

        # Name of agent team
        self.name = name
        self.agents = agents
        # Function to validate results at the end of every conversation
        self.validate_results_func = validate_results_func

        # Directory to save logs
        self.log_dir = log_dir

        # List of raw messages
        self.messages: List[str | dict] = []
        # List of chats for logging
        self.chats: List[ChatMessage] = []

    @property
    def latest_message(self) -> str | dict:
        return self.messages[-1] if self.messages else ""

    @property
    def latest_message_always_string(self) -> str:
        if isinstance(self.latest_message, dict):
            return self.latest_message.get("content", "")

        return ""

    def spy_on_agents(self):
        conversations = [dataclasses.asdict(chat) for chat in self.chats]

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        file_name = f"{self.log_dir}/{self.name}_conversations.json"
        with open(file_name, "w") as f:
            f.write(json.dumps(conversations, indent=4))

    def handle_validate_func(self) -> Tuple[bool, Optional[str]]:
        """Run the validate_results_func if it exists"""
        if self.validate_results_func:
            return self.validate_results_func()
        return True, None

    def send_message(
        self,
        from_agent: ConversableAgent,
        to_agent: ConversableAgent,
        message: str | dict,
    ):
        """Send a message from one agent to another.
        Record the message in chat log in the orchestrator
        """

        from_agent.send(message, to_agent)

        self.chats.append(
            ChatMessage(
                from_name=from_agent.name,
                to_name=to_agent.name,
                message=str(message),
            )
        )

    def has_functions(self, agent: ConversableAgent):
        return len(agent._function_map) > 0

    def basic_chat(
        self,
        agent_a: ConversableAgent,
        agent_b: ConversableAgent,
        message: str | dict,
    ):
        print(f"basic_chat(): {agent_a.name} -> {agent_b.name}")

        self.send_message(agent_a, agent_b, message)

        reply = agent_b.generate_reply(sender=agent_a)
        if reply is not None:
            self.messages.append(reply)

    def function_chat(
        self,
        agent_a: ConversableAgent,
        agent_b: ConversableAgent,
        message: str | dict,
    ):
        print(f"function_call(): {agent_a.name} -> {agent_b.name}")

        self.basic_chat(agent_a, agent_a, message)

        if isinstance(self.latest_message, dict) and "content" in self.latest_message.keys():
            self.basic_chat(agent_a, agent_b, self.latest_message)

    def self_function_chat(self, agent: ConversableAgent, message: str | dict):
        print(f"self_function_chat(): {agent.name} -> {agent.name}")

        self.send_message(agent, agent, message)

        reply = agent.generate_reply(sender=agent)

        self.send_message(agent, agent, message)

        if reply is not None:
            self.messages.append(reply)

        print(f"self_function_chat(): replied with:", reply)

    def chat(self, agent_a, agent_b, memorize=False):
        # agent_a -> chat -> agent_b
        if isinstance(self.latest_message, str):
            message = self.latest_message
            self.basic_chat(agent_a, agent_b, message)

            if memorize:
                print("Memorizing message")
                self.send_message(agent_b, agent_b, message)

        # agent_a -> func() -> agent_b
        if (
            isinstance(self.latest_message, dict)
            and "function_call" in self.latest_message
            and self.has_functions(agent_a)
        ):
            self.function_chat(agent_a, agent_b, self.latest_message)

        self.spy_on_agents()

    @staticmethod
    def validated_conversation(func):
        """Wrapper arround conversation functions that validates results at the end of every conversation"""

        def wrapper(self: Self, *args, **kwargs) -> ConversationResult:
            # Run the conversation
            func(self, *args, **kwargs)
            print(f"-------- Orchestrator Complete --------\n\n")

            was_successful, error_message = self.handle_validate_func()
            if was_successful:
                print(f"✅ Orchestrator was successful")
            else:
                print(f"❌ Orchestrator failed")

            return ConversationResult(
                messages=self.chats,
                last_message_str=self.latest_message_always_string,
                success=was_successful,
                error_message=error_message,
            )

        return wrapper

    @validated_conversation
    def sequential_conversation(self, prompt: str):
        """Runs a sequential conversation between agents.

        For example
            "Agent A" -> "Agent B" -> "Agent C" -> "Agent D" -> "Agent E"
        """
        print(f"\n\n--------- {self.name} Orchestrator Starting ---------\n\n")

        self.messages.append(prompt)

        # all agents except the last one
        for idx in range(len(self.agents) - 1):
            agent_a = self.agents[idx]
            agent_b = self.agents[idx + 1]

            print(
                f"\n\n--------- Running iteration {idx} with (agent_a: {agent_a.name}, agent_b: {agent_b.name}) ---------\n\n"
            )

            self.chat(agent_a, agent_b)

        last_agent = self.agents[-1]
        if self.latest_message and self.has_functions(last_agent):
            self.self_function_chat(last_agent, self.latest_message)

        self.spy_on_agents()

    @validated_conversation
    def broadcast_conversation(self, prompt: str):
        """Broadcast a message from agent_a to all agents.

        For example
            "Agent A" -> "Agent B"
            "Agent A" -> "Agent C"
            "Agent A" -> "Agent D"
            "Agent A" -> "Agent E"
        """

        print(f"\n\n--------- {self.name} Orchestrator Starting ---------\n\n")

        broadcast_agent = self.agents[0]
        for i, current_agent in enumerate(self.agents[1:]):
            print(
                f"\n\n--------- Running iteration {i} with (agent_broadcast: {broadcast_agent.name}, current_agent: {current_agent.name}) ---------\n\n"
            )
            self.messages.append(prompt)
            self.chat(broadcast_agent, current_agent, memorize=True)

    @validated_conversation
    def round_robin_conversation(self, prompt: str, loops: int = 1):
        """Runs a basic round robin conversation between agents:

        Example for a setup with agents A, B, and C:
            A -> B -> C -> A -> ... -> B -> C
        """
        print(f"\n\n🚀 --------- {self.name} ::: Orchestrator Starting ::: Round Robin Conversation ---------\n\n")

        for i in range(loops):
            # refeed the prompt
            self.messages.append(prompt)

            for idx in range(len(self.agents)):
                agent_a = self.agents[idx]
                agent_b = self.agents[(idx + 1) % len(self.agents)]
                print(
                    f"\n\n💬 --------- Running iteration {i} with conversation ({agent_a.name} -> {agent_b.name}) ---------\n\n",
                )

                self.chat(agent_a, agent_b)
