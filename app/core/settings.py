from pydantic import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/hackathon_db"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
