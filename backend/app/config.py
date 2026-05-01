from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_DSN: str
    API_KEY: str
    CSV_DIR = "data"

settings = Settings()