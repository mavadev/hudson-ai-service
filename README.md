<div align="center">
  <img alt="image" src="https://github.com/user-attachments/assets/d102a49f-ef59-438e-9691-07dfbffb74fc" />
</div>

### 📖 Descripción

Microservicio en **FastAPI** que conecta **Hudson AI** con **Google Gemini**. Ofrece respuestas en tiempo real mediante streaming, soporte para historial de chat, generación de títulos y un sistema inteligente de reintentos con modelos de respaldo si el servicio principal se satura.

----
### 🧪 Explorador de API

<p align="center">
  <img alt="image" src="https://github.com/user-attachments/assets/3afdc665-0a8f-4cdd-81b7-99b12fa8bf9d" />
</p>

> Explora y prueba cada endpoint interactivo mediante Swagger UI (`/docs`) y ReDoc (`/redoc`).

----
### ✨ Características

- ⚡ **Respuestas al instante**: Transmisión en tiempo real palabra por palabra mediante streaming (SSE).
- 🤖 **Google GenAI**: Integrado con el SDK oficial más reciente (`google-genai`).
- 🔄 **Modo a prueba de fallos**: Si el modelo principal se satura, reintenta automáticamente con un modelo de respaldo.
- 🛑 **Cancelación inteligente**: Si el usuario cierra el chat, detiene la generación para ahorrar recursos.
- 🏷️ **Títulos automáticos**: Crea nombres cortos para cada conversación según el primer mensaje.
- 🧠 **Manejo de contexto**: Controla el historial enviado para priorizar siempre la pregunta actual.
- 🛡️ **Errores claros**: Traduce fallas de cuotas o API keys en respuestas HTTP amigables.

----
### 🏗️ Arquitectura del proyecto

La aplicación sigue una arquitectura modular donde cada componente tiene una responsabilidad específica, facilitando el mantenimiento, la escalabilidad y la incorporación de nuevas funcionalidades.

```text
app/
├── api/          # Rutas y endpoints
├── core/         # Configuración y prompts
├── schemas/      # Modelos de datos (Pydantic)
├── services/     # Lógica con Gemini y streaming
└── main.py       # Punto de entrada y CORS
```

----
### 🚀 Endpoints disponibles

| Método | Endpoint | Descripción |
|---------|----------|-------------|
| GET | `/` | Estado base del microservicio |
| GET | `/health` | Chequeo de salud y modelo activo |
| POST | `/api/chat/title` | Generación del título del chat |
| POST | `/api/chat/stream` | Chat en vivo por streaming (SSE) |
| GET | `/docs` | Documentación interactiva Swagger |
| GET | `/redoc` | Documentación ReDoc |

----
### 💬 Ejemplo de solicitud

### 1. Streaming `POST /api/chat/stream`
### Body (JSON):

```json
{
  "user_message": "Explícame qué es una API REST",
  "history": [
      {
        "role": "user",
        "content": "Hola"
      },
      {
        "role": "assistant",
        "content": "¡Hola! ¿En qué te puedo ayudar hoy?"
      }
    ]
}
```
> **Respuesta**: Stream tipo text/event-stream que emite fragmentos de texto progresivamente.

### 2. Generación de Título `POST /api/chat/title`
### Body (JSON):

```json
{
  "user_message": "Necesito ayuda para configurar un servidor Nginx en Ubuntu"
}
```
> **Respuesta** (`200 OK`).

```json
{
  "response": "Configuración de Nginx en Ubuntu"
}
```

----
### ⚙️ Variables de entorno

Crea un archivo `.env` en la raìz del proyecto basàndote en la siguiente estructura:

```env
GEMINI_API_KEY=tu_api_key_de_google_ai
GEMINI_MODEL=gemini-2.5-flash
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000
```

----
### 💻 Instalación local

**1. Clona el repositorio:**

```bash
git clone https://github.com/mavadev/hudson-ai-service.git
cd hudson-ai-service
```

**2. Crear y activar un entorno virtual (recomendado):**

```bash
python -m venv venv
source venv/bin/activate  # En Linux/macOS
# venv\Scripts\activate   # En Windows
```

**3. Instala las dependencias:**

```bash
pip install -r requirements.txt
```

**4. Ejecuta el servidor en modo desarrollo:**

```bash
uvicorn app.main:app --reload
```

**5. El servicio estará disponible en: `http://localhost:8000`**

----
### 🌐 Despliegue & Entorno de Producción

**Servidor (Render):**
| Configuración | Valor |
|---------------|-------|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

**Tecnologías del Entorno:**

[![Stack](https://skillicons.dev/icons?i=py,fastapi,gcp)](https://skillicons.dev)

----
### 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.

Desarrollado con ❤️ por **Gianmarco Chistama**
