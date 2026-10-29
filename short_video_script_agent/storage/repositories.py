from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from ..models import ScriptResponse


class RunRepository:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, response_json TEXT NOT NULL)"
        )

    def save(self, response: ScriptResponse) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO runs(run_id, response_json) VALUES (?, ?)",
            (response.run_id, response.model_dump_json()),
        )
        self.connection.commit()

    def get(self, run_id: str) -> ScriptResponse | None:
        row = self.connection.execute(
            "SELECT response_json FROM runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        return ScriptResponse.model_validate(json.loads(row[0])) if row else None

    def close(self) -> None:
        self.connection.close()

