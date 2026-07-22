from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    user_message: str = Field(
        ...,
        min_length=1,
        max_length=10_000,
        description="Mensaje enviado por el usuario.",
        examples=["Explícame qué es una API REST."],
    )

class ChatResponse(BaseModel):
    response: str

class HealthResponse(BaseModel):
    status: str
    service: str
    provider: str
    model: str