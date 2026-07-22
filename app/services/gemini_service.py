import logging
import time

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
    ) -> str:
        delays = (2, 5, 10)

        for attempt, delay in enumerate(delays, start=1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.7,
                        top_p=0.95,
                        max_output_tokens=1_200,
                    ),
                )

                if not response.text:
                    raise RuntimeError(
                        "El proveedor de IA no devolvió contenido."
                    )

                return response.text.strip()

            except Exception as error:
                if not self._is_temporary_error(error):
                    raise

                if attempt == len(delays):
                    raise

                logger.warning(
                    "Gemini no está disponible. Reintento %s de %s en %s segundos.",
                    attempt,
                    len(delays),
                    delay,
                )

                time.sleep(delay)

        raise RuntimeError(
            "No fue posible obtener una respuesta del proveedor de IA."
        )

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


gemini_service = GeminiService()