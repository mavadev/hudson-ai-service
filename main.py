import os
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


# Cargar variables del archivo .env
load_dotenv()


# Variables de entorno
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "Falta la variable GEMINI_API_KEY en el archivo .env"
    )

# Inicializar FastAPI
app = FastAPI(
    title="AI Assistant API",
    description="Microservicio de inteligencia artificial con FastAPI y Gemini.",
    version="1.0.0",
)


# Cliente de Gemini
client = genai.Client(api_key=GEMINI_API_KEY)


# Modelo del cuerpo de la petición
class UserInput(BaseModel):
    user_message: str = Field(
        min_length=1,
        max_length=10000,
        description="Mensaje enviado por el usuario",
    )


# Prompts del sistema
PROMPT_GENERAL = (
    "Eres un asistente de inteligencia artificial experto en tecnología "
    "y programación. Responde de forma clara, precisa, profesional y "
    "amigable. Explica con ejemplos cuando sea útil."
)

PROMPT_QA = (
    "Actúa como un experto en aseguramiento de calidad de software, "
    "pruebas, casos de prueba y documentación de QA. Responde de manera "
    "profesional, detallada y estructurada."
)


import time

def call_gemini(system_prompt: str, user_message: str) -> str:
    """
    Envía el mensaje a Gemini y reintenta si el servicio está saturado.
    """
    attempts = 3
    delays = [2, 5, 10]

    for attempt in range(attempts):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    top_p=0.95,
                    max_output_tokens=1200,
                ),
            )

            if not response.text:
                raise RuntimeError("Gemini no devolvió contenido.")

            return response.text

        except Exception as error:
            message = str(error)

            is_temporary_error = (
                "503" in message
                or "UNAVAILABLE" in message
                or "high demand" in message.lower()
            )

            if not is_temporary_error or attempt == attempts - 1:
                raise

            time.sleep(delays[attempt])

    raise RuntimeError("No fue posible obtener respuesta de Gemini.")

def handle_ai_error(error: Exception) -> None:
    """
    Imprime el error completo en la terminal y devuelve una respuesta HTTP.
    """
    traceback.print_exc()

    error_name = type(error).__name__
    error_message = str(error)

    status_code = 500

    if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
        status_code = 429
    elif "401" in error_message or "API_KEY_INVALID" in error_message:
        status_code = 401
    elif "403" in error_message or "PERMISSION_DENIED" in error_message:
        status_code = 403

    raise HTTPException(
        status_code=status_code,
        detail={
            "error_type": error_name,
            "message": error_message,
        },
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "provider": "gemini",
        "model": GEMINI_MODEL,
    }


@app.post("/chat/general")
def chat_general(data: UserInput):
    try:
        response_text = call_gemini(
            system_prompt=PROMPT_GENERAL,
            user_message=data.user_message,
        )

        return {"response": response_text}

    except Exception as error:
        handle_ai_error(error)


@app.post("/chat/qa")
def chat_qa(data: UserInput):
    try:
        response_text = call_gemini(
            system_prompt=PROMPT_QA,
            user_message=data.user_message,
        )

        return {"response": response_text}

    except Exception as error:
        handle_ai_error(error)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )