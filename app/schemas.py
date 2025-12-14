from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default="")
    channel: Optional[str] = Field(default="web")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    quick_replies: List[str]
    state: str
    context: Dict[str, Any]


class SessionSchema(BaseModel):
    id: str
    state: str
    context: Dict[str, Any]

    class Config:
        from_attributes = True

