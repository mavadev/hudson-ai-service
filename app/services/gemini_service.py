import asyncio
import logging
from typing import AsyncGenerator, List, Optional

from fastapi import Request
from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.chat import MessageItem

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    async def _call_genai(
        self, model: str, system_prompt: str, user_message: str
    ) -> str:
        delays = (2, 5, 10)
        for attempt, delay in enumerate(delays, start=1):
            try:
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.7,
                        top_p=0.95,
                        max_output_tokens=1_200,
                    ),
                )
                if not response.text:
                    raise RuntimeError("El proveedor de IA no devolvió contenido.")
                return response.text.strip()
            except Exception as error:
                if not self._is_temporary_error(error) or attempt == len(delays):
                    raise error
                await asyncio.sleep(delay)

    @staticmethod
    def _is_temporary_error(error: Exception) -> bool:
        message = str(error).lower()
        temporary_markers = (
            "429",
            "503",
            "resource_exhausted",
            "unavailable",
            "high demand",
            "deadline exceeded",
            "timeout",
        )
        return any(marker in message for marker in temporary_markers)

    async def generate_title_response(
        self,
        system_prompt: str,
        user_message: str,
    ) -> str:
        # Intentar primero con el modelo configurado
        try:
            return await self._call_genai(self.model, system_prompt, user_message)
        except Exception as error:
            if self._is_temporary_error(error):
                logger.warning(
                    "Modelo principal saturado. Usando modelo de respaldo..."
                )
                # Fallback a un modelo alternativo
                return await self._call_genai(
                    "gemini-3.8-flash", system_prompt, user_message
                )
            raise error

    async def generate_stream_response(
        self,
        system_prompt: str,
        user_message: str,
        history: List[MessageItem] = None,
        max_history_turns: int = 10,
        request: Optional[Request] = None,
    ) -> AsyncGenerator[str, None]:
        delays = (2, 5, 10)
        models_to_try = [self.model, "gemini-2.5-flash", "gemini-1.5-flash"]
        formatted_contents = []

        # Recortamos el historial para mantener solo los últimos N mensajes
        recent_history = history[-max_history_turns:] if history else []

        # Agregamos el historial previo como contexto general
        if recent_history:
            for msg in recent_history:
                if msg.content and msg.content.strip():
                    role = "model" if msg.role in ["assistant", "model"] else "user"
                    formatted_contents.append(
                        {"role": role, "parts": [{"text": msg.content.strip()}]}
                    )

        # Enfatizamos el mensaje actual del usuario
        if user_message and user_message.strip():
            # Si hay historial, le marcamos explícitamente la prioridad
            if recent_history:
                prompt_with_focus = (
                    f"[Atención: Responde prioritariamente a la siguiente consulta actual del usuario. "
                    f"Utiliza el historial anterior únicamente como contexto secundario o de referencia]:\n\n"
                    f"{user_message.strip()}"
                )
            else:
                prompt_with_focus = user_message.strip()

            formatted_contents.append(
                {"role": "user", "parts": [{"text": prompt_with_focus}]}
            )

        if not formatted_contents:
            yield "El mensaje recibido está vacío."
            return

        # Petición a Gemini
        for model_name in models_to_try:
            for attempt, delay in enumerate(delays, start=1):
                try:
                    response = await self.client.aio.models.generate_content_stream(
                        model=model_name,
                        contents=formatted_contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=0.7,
                            top_p=0.95,
                            max_output_tokens=1_200,
                        ),
                    )
                    # Consumimos e iteramos los fragmentos
                    async for chunk in response:
                        # Verificar si el cliente canceló la conexión
                        if request and await request.is_disconnected():
                            logger.info(
                                "[FastAPI] El cliente canceló la solicitud. Abortando stream."
                            )
                            return

                        if chunk.text:
                            yield chunk.text
                    # Si completó el stream con éxito, salimos de la función
                    return

                except Exception as error:
                    # Evitar reintentos si la razón de la falla fue la desconexión
                    if request and await request.is_disconnected():
                        return

                    if not self._is_temporary_error(error):
                        raise

                    logger.warning(
                        "Gemini (%s) no disponible (Intento %s/%s). Esperando %ss...",
                        model_name,
                        attempt,
                        len(delays),
                        delay,
                    )

                    if attempt < len(delays):
                        await asyncio.sleep(delay)

            logger.warning(
                "El modelo %s falló tras varios reintentos. Probando modelo alternativo...",
                model_name,
            )
        # Si todos los modelos fallan
        yield "El servicio de IA se encuentra actualmente saturado. Por favor, intente de nuevo en unos momentos."


gemini_service = GeminiService()
