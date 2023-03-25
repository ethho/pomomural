from pydantic import BaseSettings

class Settings(BaseSettings):
    ORS_KEY: str
    PORT: int
    MAX_RESULTS: int = 10

    class Config:
        env_file = ".env"

settings = Settings()
