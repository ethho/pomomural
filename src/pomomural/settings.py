from pydantic import BaseSettings

class Settings(BaseSettings):
    ORS_KEY: str
    PORT: int
    MAX_RESULTS: int = 10
    MURAL_CSV_FP: str = 'data/mural.csv'

    class Config:
        env_file = ".env"

settings = Settings()
