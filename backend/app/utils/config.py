from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Supabase
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")

    # Google Cloud
    google_cloud_project_id: Optional[str] = Field(None, env="GOOGLE_CLOUD_PROJECT_ID")
    google_application_credentials: Optional[str] = Field(None, env="GOOGLE_APPLICATION_CREDENTIALS")

    # 評価設定
    default_skill_ratio: float = Field(0.2, env="DEFAULT_SKILL_RATIO")
    default_mindset_ratio: float = Field(0.8, env="DEFAULT_MINDSET_RATIO")

    # API設定
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")

    # セキュリティ
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
