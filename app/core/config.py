import os

from dotenv import load_dotenv
from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    gemini_api_key: str
    gemini_model: str = "gemini-3.8-flash"
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @model_validator(mode="after")
    def validate_api_key(self) -> "Settings":
        if not self.gemini_api_key or not self.gemini_api_key.strip():
            raise RuntimeError(
                "La variable de entorno GEMINI_API_KEY no está configurada en el archivo .env."
            )
        return self


settings = Settings()
