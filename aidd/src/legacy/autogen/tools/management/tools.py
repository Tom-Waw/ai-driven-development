from typing import Annotated, Literal

from autogen import GroupChat, GroupChatManager
from lpu.standard import base_config
from pydantic import BaseModel
from tools.registry import ToolRegistry

management = ToolRegistry()


### Meetings ###


class MeetingTopic(BaseModel):
    title: str
    motivation: Annotated[str, "The reason for discussing this topic."]
    goal: Annotated[str, "The information you want to gain from discussing this topic."]


class MeetingPlan(BaseModel):
    goal: Annotated[str, "The overall goal or reason for the meeting."]
    topics: Annotated[list[MeetingTopic], "The topics you want to discuss."]


# def start_meeting(
#     participant: Literal["software_engineer", "developer", "all"],
#     meeting_plan: MeetingPlan,
# ) -> str:
#     """Start a meeting with one or more participants."""
#     # ? Prevent nested calling
#     project_manager.update_tool_signature(start_meeting.__name__, is_remove=True)

#     agents = []

#     if participant == "software_engineer":
#         agents.append(software_engineer)
#     elif participant == "developer":
#         agents.append(developer)
#     elif participant == "all":
#         agents.extend([software_engineer, developer])

#     group_chat = GroupChat(
#         agents=[project_manager, *agents],
#         messages=[],
#         max_round=50,
#         speaker_selection_method="auto",
#     )
#     group_chat_manager = GroupChatManager(groupchat=group_chat, llm_config=base_config)

#     result = thoughts.initiate_chat(
#         recipient=group_chat_manager,
#         message="New meeting started.",
#         clear_history=False,
#         summary_method="reflection_with_llm",
#         summary_args={
#             "summary_prompt": "Conclude the outcome of the meeting. What are the next steps?",
#         },
#     )

#     # result = project_manager.initiate_chat(
#     #     recipient=agent,
#     #     message="I need your expertise to go forward with the project.",
#     #     clear_history=False,
#     #     max_turns=50,
#     #     summary_method="reflection_with_llm",
#     #     summary_args={
#     #         "summary_prompt": "Conclude the outcome of the meeting. What are the next steps?",
#     #     },
#     # )

#     # ? Summary will be preserved, forget the conversation history
#     project_manager.clear_history(recipient=software_engineer)

#     register_meetings_for_pm(start_meeting)
#     return result.summary
