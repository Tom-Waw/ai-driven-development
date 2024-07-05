import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class ChatMessage:
    from_name: str
    to_name: str
    message: str
    created: float = field(default_factory=time.time)


@dataclass
class ConversationResult:
    messages: List[ChatMessage]
    last_message_str: str
    success: bool
    error_message: str | None = None
