import json
from pathlib import Path


class VerifiedFacts:
    FILE = Path("knowledge/runtime/verified_facts.json")

    def load(self) -> dict:
        if not self.FILE.exists():
            return {}

        return json.loads(self.FILE.read_text(encoding="utf-8"))

    def save(self, facts: dict) -> None:
        self.FILE.parent.mkdir(parents=True, exist_ok=True)
        self.FILE.write_text(
            json.dumps(facts, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
