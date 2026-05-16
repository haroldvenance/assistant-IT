from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        from_attributes = True   # <-- Changé ici

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    class Config:
        from_attributes = True

# Les autres schémas restent inchangés
class UserCreate(BaseModel):
    username: str
    password: str

class ConversationCreate(BaseModel):
    title: Optional[str] = "Nouvelle conversation"

class ConversationUpdate(BaseModel):
    title: str

class ChatRequest(BaseModel):
    conversation_id: int
    message: str
    model: str