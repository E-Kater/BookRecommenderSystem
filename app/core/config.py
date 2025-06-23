from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Book Recommender System"
    debug: bool = False
    DB_HOST: str = "postgres"
    DB_PORT: str = "5432"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "bookdb"

    class Config:
        env_file = ".env"


settings = Settings()
