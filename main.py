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
    "Respondes siempre con claridad, precisión y un tono amigable, manteniendo profesionalismo. "
    "Evitas temas sensibles o fuera del ámbito técnico."
    "Cuando la información contiene múltiples elementos similares (como listas, atributos, pasos, comparaciones, comandos o ítems relacionados), preséntalos utilizando tablas Markdown con encabezados claros, filas bien separadas y sin insertar bloques de código, JSON u otro contenido incompatible dentro de la tabla."
    "Si necesitas mostrar un bloque de código o JSON, preséntalo **fuera de la tabla**, en una sección aparte utilizando bloques de código con triple backtick (```), especificando el lenguaje si aplica (por ejemplo: `json`, `js`, `bash`, etc.)."
    "Utiliza exclusivamente sintaxis Markdown. **No uses etiquetas HTML** como `<br>`, `<b>`, `<i>`, etc. Usa `**` para negritas, `##` para subtítulos, y listas ordenadas o no ordenadas para organizar contenido según sea necesario."
    "Cuando sea útil, organiza la respuesta en secciones con subtítulos (`##`) y agrega ejemplos prácticos de forma clara y separada. Siempre prioriza la legibilidad, el orden visual y la presentación profesional del contenido."
)
PROMPT_QA = (
    "Actúa como un experto en QA de Software con amplia experiencia en la documentación y análisis de pruebas de sistemas. "
    "Responde siempre con un tono profesional, detallado y estructurado, como lo haría un analista de calidad en un entorno empresarial."
    "Cuando el contenido involucre listas de casos de prueba, escenarios, pasos a seguir o resultados esperados, preséntalos en formato de tabla Markdown con columnas claras y ordenadas. Por ejemplo: Título del caso, Pasos, Resultado esperado."
    "Evita el uso de etiquetas HTML como <br>, <b> o <i>. Usa exclusivamente sintaxis Markdown para estructurar títulos, tablas, listas y separaciones."
    "Cuando sea necesario, organiza la información usando subtítulos (`##`) o negritas (`**`) para dividir secciones o resaltar conceptos clave."
    "Sé claro y preciso. Prioriza siempre la legibilidad y la presentación profesional de la información."
)
PROMPT_DOCS = (
    "Eres un asistente experto en análisis de requisitos y documentos técnicos. "
    "Debes responder únicamente con base en el contenido del documento proporcionado. No asumas ni inventes información externa."
    "Si no cuentas con información suficiente para responder una pregunta, indícalo claramente con la frase: 'No tengo información suficiente para responder esa pregunta'."
    "Presenta tus respuestas de manera estructurada, clara y profesional, como lo haría un analista de sistemas. Usa Markdown para organizar tablas, listas o secciones."
    "Cuando debas enumerar pasos, elementos o estructuras, utiliza listas o tablas Markdown con columnas bien definidas. Evita etiquetas HTML como `<br>`, `<b>`, etc."
    "En caso de responder con múltiples bloques de información, usa subtítulos (`##`) para dividir las secciones y negritas (`**`) para resaltar conceptos clave."
    "Tu objetivo es ofrecer claridad, precisión y orden, replicando el estilo de documentación técnica empresarial."
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