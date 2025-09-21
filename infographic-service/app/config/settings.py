import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class GCPConfig:
    project_id: str
    location: str
    google_api_key: str
    bucket_name: str
    use_vertex_ai: str
    subscription_name: str
    output_topic_name: str
    credentials_path: Optional[str] = None


@dataclass
class ServiceConfig:
    max_workers: int = 4
    timeout_seconds: int = 300
    log_level: str = "INFO"
    model_name: str = "gemini-2.5-flash"


@dataclass
class AgentConfig:
    app_name: str = "startup_analysis_agent"
    user_id: str = "analysis_service"
    session_id_prefix: str = "session"


class Settings:
    def __init__(self):
        self.gcp = GCPConfig(
            project_id=self._get_required_env("GOOGLE_CLOUD_PROJECT"),
            location=self._get_required_env("GOOGLE_CLOUD_LOCATION"),
            google_api_key=self._get_required_env("GOOGLE_API_KEY"),
            bucket_name=self._get_required_env("BUCKET_NAME"),
            use_vertex_ai=self._get_required_env("GOOGLE_GENAI_USE_VERTEXAI"),
            subscription_name=self._get_required_env("PUBSUB_SUBSCRIPTION_NAME"),
            output_topic_name=self._get_required_env("PUBSUB_OUTPUT_TOPIC_NAME"),
            credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        )
        
        self.service = ServiceConfig(
            max_workers=int(os.getenv("MAX_WORKERS", "4")),
            timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "300")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            model_name=os.getenv("MODEL_NAME", "gemini-2.5-flash"),
        )
        
        self.agent = AgentConfig(
            app_name=os.getenv("AGENT_APP_NAME", "startup_analysis_agent"),
            user_id=os.getenv("AGENT_USER_ID", "analysis_service"),
            session_id_prefix=os.getenv("AGENT_SESSION_PREFIX", "session"),
        )
    
    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value


settings = Settings()
