from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

STATE_FILE = Path.home() / ".atbclone" / "clones.yaml"


@dataclass
class CloneRecord:
    clone_name: str
    source_app: str
    source_path: str
    bundle_id: str
    strategy: str
    dest_path: str
    data_dir: str
    created_at: str
    proxy_enabled: bool = False
    proxy_summary: str = ""
    new_bundle_id: str = ""


class StateManager:
    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = Path(state_file)

    def load(self) -> list[CloneRecord]:
        """Load all records from YAML file. Returns empty list if file missing or corrupt."""
        if not self.state_file.exists():
            return []
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except (yaml.YAMLError, OSError):
            return []

        if not isinstance(data, list):
            return []

        records: list[CloneRecord] = []
        for item in data:
            if isinstance(item, dict):
                try:
                    records.append(CloneRecord(**item))
                except TypeError:
                    continue
        return records

    def save(self, records: list[CloneRecord]) -> None:
        """Save records to YAML file (create parent dirs if needed)."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        raw_list = [asdict(r) for r in records]
        with open(self.state_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(raw_list, f, allow_unicode=True, sort_keys=False)

    def add(self, record: CloneRecord) -> None:
        """Append or update a record and persist."""
        records = self.load()
        for i, r in enumerate(records):
            if r.clone_name == record.clone_name:
                records[i] = record
                break
        else:
            records.append(record)
        self.save(records)

    def remove(self, clone_name: str) -> bool:
        """Remove record by clone_name. Returns True if found and removed."""
        records = self.load()
        new_records = [r for r in records if r.clone_name != clone_name]
        if len(new_records) != len(records):
            self.save(new_records)
            return True
        return False

    def get(self, clone_name: str) -> CloneRecord | None:
        """Get record by clone_name. Returns None if not found."""
        for r in self.load():
            if r.clone_name == clone_name:
                return r
        return None
