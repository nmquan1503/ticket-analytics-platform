from pydantic_settings import BaseSettings
from typing  import ClassVar

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_DSN: str
    API_KEY: str
    CSV_DIR: ClassVar[str] = "data"

settings = Settings()