from pydantic_settings import BaseSettings  # <---- NEW import
from pydantic import AnyUrl, Field


class Settings(BaseSettings):
    MONGO_URI: AnyUrl = Field("mongodb://localhost:27017", env="MONGO_URI")
    MONGO_DB_NAME: str = Field("assessment_db", env="MONGO_DB_NAME")
    CREATE_COLLECTION_VALIDATOR: bool = Field(False, env="CREATE_COLLECTION_VALIDATOR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
