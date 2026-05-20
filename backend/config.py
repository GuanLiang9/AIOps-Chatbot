from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    LOG_LEVEL: str = "INFO"
    MAX_CHAT_HISTORY: int = 20

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
