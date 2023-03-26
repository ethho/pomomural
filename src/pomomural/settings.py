from pydantic import BaseSettings

class Settings(BaseSettings):
    ORS_KEY: str
    PORT: int
    MAX_RESULTS: int = 6
    MURAL_CSV_FP: str = 'data/mural.csv'
    NOT_FOUND_IMG: str = 'https://i.ibb.co/Bc2Cs0V/crusty.jpg'

    class Config:
        env_file = ".env"

settings = Settings()
