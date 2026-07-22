import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    gemini_api_key: str
    gemini_model: str
    environment: str

    def __init__(self) -> None:
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.environment = os.getenv("ENVIRONMENT", "development")

        if not self.gemini_api_key:
            raise RuntimeError(
                "La variable de entorno GEMINI_API_KEY no está configurada."
            )


settings = Settings()