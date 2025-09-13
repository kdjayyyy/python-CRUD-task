from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    MONGO_URI: str = Field("mongodb://localhost:27017", env="MONGO_URI")
    MONGO_DB_NAME: str = Field("assessment_db", env="MONGO_DB_NAME")
    CREATE_COLLECTION_VALIDATOR: bool = Field(False, env="CREATE_COLLECTION_VALIDATOR")

    # JWT settings
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Admin credentials (hash stored)
    ADMIN_USERNAME: str = Field(..., env="ADMIN_USERNAME")
    ADMIN_PASSWORD_HASH: str = Field(..., env="ADMIN_PASSWORD_HASH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
