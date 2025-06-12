from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar FastAPI
app = FastAPI()

# Cliente de Azure OpenAI
client = AzureOpenAI(
    azure_endpoint=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2025-01-01-preview",
)

# Clase para el input del usuario
class UserInput(BaseModel):
    user_message: str

# Prompts (los centralizamos)
PROMPT_GENERAL = (
    "Eres un asistente de inteligencia artificial experto en tecnología y programación. "
    "Respondes de forma clara, precisa, profesional y con un tono amigable. Evitas temas sensibles o fuera del ámbito técnico. "
    "Siempre explicas con ejemplos si es necesario."
)
PROMPT_QA = (
    "Actúa como un experto en QA de Software con amplia experiencia en la creación de documentación de pruebas. "
    "Responde siempre con un nivel profesional, detallado y estructurado."
)
PROMPT_DOCS = (
    "Eres un asistente experto en análisis de requisitos y documentos técnicos. "
    "Solo respondes con base en el contenido del documento proporcionado. "
    "Si no sabes algo, responde 'no tengo información suficiente para responder esa pregunta'."
)

# Función genérica para enviar a Azure OpenAI
def call_openai(messages, extra_body=None):
    return client.chat.completions.create(
        model=os.getenv("DEPLOYMENT_NAME"),
        messages=messages,
        max_tokens=2000,
        temperature=0.7,
        top_p=0.95,
        extra_body=extra_body
    )

# Healthcheck
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Chat General
@app.post("/chat/general")
def chat_general(input: UserInput):
    try:
        messages = [
            {"role": "system", "content": PROMPT_GENERAL},
            {"role": "user", "content": input.user_message}
        ]
        response = call_openai(messages)
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat QA
@app.post("/chat/qa")
def chat_qa(input: UserInput):
    try:
        messages = [
            {"role": "system", "content": PROMPT_QA},
            {"role": "user", "content": input.user_message}
        ]
        response = call_openai(messages)
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat basado en documentos
@app.post("/chat/docs")
def chat_by_doc(input: UserInput):
    try:
        messages = [
            {"role": "system", "content": PROMPT_DOCS},
            {"role": "user", "content": input.user_message}
        ]
        extra_body = {
            "data_sources": [{
                "type": "azure_search",
                "parameters": {
                    "endpoint": os.getenv("SEARCH_ENDPOINT"),
                    "index_name": os.getenv("SEARCH_INDEX_NAME"),
                    "semantic_configuration": "default",
                    "query_type": "semantic",
                    "filter": "title eq 'HU108.pdf'",
                    "strictness": 3,
                    "top_n_documents": 5,
                    "authentication": {
                        "type": "api_key",
                        "key": os.getenv("SEARCH_KEY")
                    }
                }
            }]
        }
        response = call_openai(messages, extra_body=extra_body)
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))