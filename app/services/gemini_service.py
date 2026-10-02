import asyncio
import logging
from typing import AsyncGenerator, List

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

    async def generate_response(
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
                    "gemini-2.5-flash", system_prompt, user_message
                )
            raise error

    async def generate_stream_response(
        self,
        system_prompt: str,
        user_message: str,
        history: List[MessageItem] = None,
    ) -> AsyncGenerator[str, None]:
        delays = (2, 5, 10)
        models_to_try = [self.model, "gemini-2.5-flash", "gemini-1.5-flash"]

        formatted_contents = []

        if history:
            for msg in history:
                # Convertimos el rol de assistant a model
                role = "model" if msg.role in ["assistant", "model"] else "user"
                formatted_contents.append(
                    types.Content(
                        role=role, parts=[types.Part.from_text(text=msg.content)]
                    )
                )

            # Añadimos el mensaje actual del usuario al final del historial
            formatted_contents.append(
                types.Content(
                    role="user", parts=[types.Part.from_text(text=user_message)]
                )
            )

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
                        if chunk.text:
                            yield chunk.text
                    # Si completó el stream con éxito, salimos de la función
                    return

                except Exception as error:
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
