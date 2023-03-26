from pydantic import BaseSettings

class Settings(BaseSettings):
    ORS_KEY: str
    PORT: int
    MAX_RESULTS: int = 10
    MURAL_CSV_FP: str = 'data/mural.csv'
    NOT_FOUND_IMG: str = 'https://imgur.com/a/rE1wVTl'

    class Config:
        env_file = ".env"

settings = Settings()
