from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    message: str

class ChatResponse(BaseModel):
    session_id: int
    reply: str

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}

class SessionOut(BaseModel):
    id: int
    created_at: datetime
    messages: List[MessageOut]

    model_config = {"from_attributes": True}
