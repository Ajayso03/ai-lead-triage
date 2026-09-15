"""
Configuration module for the Inbound Lead Triage & Operator Card Workflow.
Loads environment variables safely and defines runtime parameters.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env if present
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class WorkflowConfig(BaseModel):
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"))
    execution_mode: str = Field(default_factory=lambda: os.getenv("EXECUTION_MODE", "auto").lower())
    telegram_bot_token: str = Field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = Field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))
    slack_webhook_url: str = Field(default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL", ""))
    enterprise_threshold: int = Field(default_factory=lambda: int(os.getenv("ENTERPRISE_THRESHOLD", "75")))
    max_timeout_seconds: int = 15

    @property
    def has_live_api_key(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip() != "your_openai_api_key_here")

    @property
    def should_use_live_api(self) -> bool:
        if self.execution_mode == "live":
            return True
        if self.execution_mode == "auto":
            return self.has_live_api_key
        return False


config = WorkflowConfig()
