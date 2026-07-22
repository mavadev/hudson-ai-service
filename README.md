<div align="center">
  <img width="1774" height="887" alt="image" src="https://github.com/user-attachments/assets/d102a49f-ef59-438e-9691-07dfbffb74fc" />
</div>

## 📖 Descripción

Hudson AI Service es un microservicio desarrollado con **FastAPI** que integra **Google Gemini** para ofrecer capacidades conversacionales mediante una API REST moderna, documentada y preparada para producción.

Su arquitectura modular facilita el mantenimiento, la escalabilidad y la integración con aplicaciones frontend.

## 🧪 Explorador de API

<p align="center">
  <img width="1579" height="996" alt="image" src="https://github.com/user-attachments/assets/beff6ad2-b42a-444a-a9fc-936ff49fb094" />
</p>

> Explora y prueba cada endpoint del servicio mediante la documentación interactiva.

## ✨ Características

- ✅ API REST desarrollada con FastAPI.
- ✅ Integración con Google Gemini.
- ✅ Asistente conversacional de propósito general.
- ✅ Endpoint especializado en consultas de QA.
- ✅ Documentación automática mediante Swagger y ReDoc.
- ✅ Arquitectura modular y escalable.
- ✅ Configuración mediante variables de entorno.
- ✅ Reintentos automáticos ante errores temporales del proveedor.
- ✅ Gestión centralizada de prompts.
- ✅ Preparado para despliegues en producción.

## 🏗️ Arquitectura del proyecto

La aplicación sigue una arquitectura modular donde cada componente tiene una responsabilidad específica, facilitando el mantenimiento, la escalabilidad y la incorporación de nuevas funcionalidades.

```text
app/
├── api/
├── core/
├── schemas/
├── services/
└── main.py
```

| Carpeta | Descripción |
|----------|-------------|
| **api** | Contiene los endpoints de la API. |
| **services** | Implementa la comunicación con Google Gemini. |
| **schemas** | Modelos de validación de solicitudes y respuestas. |
| **core** | Configuración general y prompts del sistema. |

## 🚀 Endpoints disponibles

| Método | Endpoint | Descripción |
|---------|----------|-------------|
| GET | `/` | Información del servicio |
| GET | `/health` | Estado del servicio |
| POST | `/chat/general` | Asistente conversacional |
| POST | `/chat/qa` | Asistente especializado en QA |
| GET | `/docs` | Documentación Swagger |
| GET | `/redoc` | Documentación ReDoc |

## 💬 Ejemplo de solicitud

### POST `/chat/general`

```json
{
  "user_message": "¿Qué es una API REST?"
}
```

## ✅ Ejemplo de respuesta

```json
{
  "response": "Una API REST permite que diferentes aplicaciones se comuniquen entre sí mediante solicitudes HTTP utilizando recursos y métodos estándar como GET, POST, PUT y DELETE"
}
```

## ⚙️ Variables de entorno

Crea un archivo `.env` con las siguientes variables:

```env
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.5-flash
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000
```

## 💻 Instalación local

Clona el repositorio:

```bash
git clone https://github.com/mavadev/hudson-ai-service.git
cd hudson-ai-service
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Ejecuta el servidor:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://localhost:8000
```

Documentación Swagger:

```text
http://localhost:8000/docs
```

Documentación ReDoc:

```text
http://localhost:8000/redoc
```

## 🌐 Despliegue

El proyecto está preparado para desplegarse fácilmente en **Render**.

| Configuración | Valor |
|---------------|-------|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |


## 🔮 Mejoras futuras

- Respuestas en streaming.
- Memoria conversacional.
- Carga y análisis de archivos.
- Métricas de consumo y rendimiento.

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.

<div align="center">

Desarrollado con ❤️ por **Gianmarco Chistama**

</div>
