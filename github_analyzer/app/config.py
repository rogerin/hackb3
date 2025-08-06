from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    github_client_id: str
    github_client_secret: str
    openai_api_key: str
    gemini_api_key: str
    webhook_secret: str
    session_secret_key: str
    base_url: str = "http://127.0.0.1:8088"  # URL base da aplicação (será substituída pelo ngrok)

    class Config:
        # Construir o caminho absoluto para o arquivo .env
        # Isso garante que ele seja encontrado independentemente do diretório de trabalho atual
        env_file = Path(__file__).parent.parent / ".env"
        extra = 'ignore'

settings = Settings()
