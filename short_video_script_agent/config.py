from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    base_url: str | None
    model: str | None
    api_mode: str

    @property
    def llm_configured(self) -> bool:
        return bool(
            self.api_key
            and self.base_url
            and self.model
            and self.api_mode in {"responses", "chat_completions"}
        )

    @classmethod
    def from_environment(cls, dotenv_path: Path | None = None) -> "Settings":
        load_dotenv(dotenv_path=dotenv_path, override=False)
        return cls(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            model=os.getenv("LLM_MODEL"),
            api_mode=os.getenv("LLM_API_MODE", "responses"),
        )
