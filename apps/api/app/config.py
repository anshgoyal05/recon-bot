from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union, Optional
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Recon-Bot API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # AI / Vision
    GEMINI_API_KEY: Optional[str] = ""

    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/recon_bot.db"

    # Storage paths
    STORAGE_DIR: Path = BASE_DIR.parent / "storage"
    SAMPLE_DATA_DIR: Path = BASE_DIR.parent / "sample_data"

    # Default Buyer Company Settings
    COMPANY_NAME: str = "Precision Auto Components Pvt Ltd"
    COMPANY_GSTIN: str = "27AAACP1234M1ZG"
    COMPANY_STATE_CODE: str = "27"
    COMPANY_STATE: str = "Maharashtra"

    # Reconciliation Tolerances
    QTY_TOLERANCE_PCT: float = 2.0
    PRICE_TOLERANCE_INR: float = 0.01
    PRICE_TOLERANCE_PCT: float = 0.5
    TAX_ROUNDOFF_TOLERANCE_INR: float = 1.0

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
