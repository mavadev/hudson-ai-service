import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.prompts import PROMPT_GENERAL, PROMPT_QA
from app.schemas.chat import ChatRequest, ChatResponse, HealthResponse
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

router = APIRouter()
@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="hudson-ai-service",
        provider="gemini",
        model=settings.gemini_model,
    )

@router.post(
    "/chat/general",
    response_model=ChatResponse,
    tags=["Chat"],
)
async def chat_general(data: ChatRequest) -> ChatResponse:
    return await generate_ai_response(
        system_prompt=PROMPT_GENERAL,
        user_message=data.user_message,
    )

@router.post("/chat/general/stream", tags=["Chat"])
async def chat_general_stream(data: ChatRequest):
    return StreamingResponse(
        gemini_service.generate_stream_response(
            system_prompt=PROMPT_GENERAL,
            user_message=data.user_message,
        ),
        media_type="text/event-stream",
    )

@router.post(
    "/chat/qa",
    response_model=ChatResponse,
    tags=["Chat"],
)
async def chat_qa(data: ChatRequest) -> ChatResponse:
    return await generate_ai_response(
        system_prompt=PROMPT_QA,
        user_message=data.user_message,
    )

async def generate_ai_response(
    system_prompt: str,
    user_message: str,
) -> ChatResponse:
    try:
        response = await gemini_service.generate_response(
            system_prompt=system_prompt,
            user_message=user_message,
        )
        return ChatResponse(response=response)

    except Exception as error:
        logger.exception("Error al generar la respuesta de IA.")
        raise map_ai_error(error) from error


def map_ai_error(error: Exception) -> HTTPException:
    error_message = str(error)
    normalized_message = error_message.lower()

    if "429" in normalized_message or "resource_exhausted" in normalized_message:
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="El servicio de IA alcanzó temporalmente su límite de solicitudes.",
        )

    if "401" in normalized_message or "api_key_invalid" in normalized_message:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El proveedor de IA no está configurado correctamente.",
        )

    if "403" in normalized_message or "permission_denied" in normalized_message:
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El proveedor de IA rechazó la solicitud.",
        )

    if "503" in normalized_message or "unavailable" in normalized_message:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de IA no está disponible temporalmente.",
        )

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Ocurrió un error al procesar la solicitud.",
    )