from dataclasses import asdict, dataclass
from pathlib import Path
import os

import yaml

from atbclone.core.config import DEFAULT_STATE_FILE

STATE_FILE = DEFAULT_STATE_FILE


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
    language: str = "system"
    display_name: str | None = None
    injection_strategy: str = "auto"


class StateManager:
    def __init__(self, state_file: Path | None = None):
        if state_file is not None:
            self.state_file = Path(state_file)
        else:
            from atbclone.core.config import DEFAULT_STATE_FILE
            self.state_file = DEFAULT_STATE_FILE

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
        dirty = False
        for item in data:
            if isinstance(item, dict):
                if "language" not in item or not item["language"]:
                    item["language"] = "system"
                if "injection_strategy" not in item or not item["injection_strategy"]:
                    item["injection_strategy"] = "auto"
                try:
                    rec = CloneRecord(**item)
                    # Migrate legacy embedded password from proxy_summary to Keychain
                    if rec.proxy_enabled and rec.proxy_summary:
                        try:
                            from urllib.parse import urlparse
                            parsed = urlparse(rec.proxy_summary)
                            if parsed.password:
                                from atbclone.core.keychain import save_clone_proxy_password
                                save_clone_proxy_password(rec.clone_name, parsed.password)
                                user_info = f"{parsed.username}@" if parsed.username else ""
                                host_info = parsed.hostname or ""
                                if parsed.port:
                                    host_info = f"{host_info}:{parsed.port}"
                                rec.proxy_summary = f"{parsed.scheme}://{user_info}{host_info}"
                                dirty = True
                        except Exception:
                            pass
                    records.append(rec)
                except TypeError:
                    continue

        if dirty:
            self.save(records)
        return records

    def save(self, records: list[CloneRecord]) -> None:
        """Save records to YAML file (create parent dirs if needed)."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        # Ensure no plaintext passwords exist in records before saving
        for r in records:
            if r.proxy_enabled and r.proxy_summary:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(r.proxy_summary)
                    if parsed.password:
                        from atbclone.core.keychain import save_clone_proxy_password
                        save_clone_proxy_password(r.clone_name, parsed.password)
                        user_info = f"{parsed.username}@" if parsed.username else ""
                        host_info = parsed.hostname or ""
                        if parsed.port:
                            host_info = f"{host_info}:{parsed.port}"
                        r.proxy_summary = f"{parsed.scheme}://{user_info}{host_info}"
                except Exception:
                    pass

        raw_list = [asdict(r) for r in records]
        with open(self.state_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(raw_list, f, allow_unicode=True, sort_keys=False)
        # Records may embed proxy credentials in proxy_summary; keep the file
        # owner-readable only.
        try:
            os.chmod(self.state_file, 0o600)
        except OSError:
            pass

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
            try:
                from atbclone.core.keychain import delete_clone_proxy_password
                delete_clone_proxy_password(clone_name)
            except Exception:
                pass
            return True
        return False

    def get(self, clone_name: str) -> CloneRecord | None:
        """Get record by clone_name. Returns None if not found."""
        for r in self.load():
            if r.clone_name == clone_name:
                return r
        return None
