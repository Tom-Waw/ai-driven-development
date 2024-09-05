from pydantic import BaseModel


class ReasoningStep(BaseModel):
    explanation: str
    output: str


class ChainOfThoughts(BaseModel):
    reasoning_steps: list[ReasoningStep]
    final_answer: str
