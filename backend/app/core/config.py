import os
from typing import List
from pathlib import Path
from dotenv import load_dotenv

# Try loading from .env or backend/.env
env_paths = [Path(".env"), Path("backend/.env"), Path("../.env")]
for p in env_paths:
    if p.exists():
        load_dotenv(p)
        break

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Public Transport Route Helper for India")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./transit_app.db")

    # AI (Mistral AI)
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "codestral-latest")
    # Legacy Gemini fallback compatibility if configured
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # ML
    ML_MODEL_DIR: str = os.getenv("ML_MODEL_DIR", "ml/artifacts")
    DEFAULT_DELAY_MODEL: str = os.getenv("DEFAULT_DELAY_MODEL", "hist_gradient_boosting_v1.joblib")

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
