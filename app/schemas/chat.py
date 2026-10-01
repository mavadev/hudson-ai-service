from typing import List, Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str
    service: str
    provider: str
    model: str

class ChatRequest(BaseModel):
    user_message: str = Field(
        ...,
        min_length=1,
        max_length=10_000,
        description="Mensaje enviado por el usuario.",
        examples=["Explícame qué es una API REST."],
    ),
    history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    response: str

class Message(BaseModel):
    role: str
    content: str


ChatRequest.model_rebuild()