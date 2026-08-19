import yaml  # type: ignore[import-untyped]
from pathlib import Path
from .models import Recipe


class RecipeLoader:
    BUILTIN_DIR = Path(__file__).parent / "builtin"
    LOCAL_DIR: Path | None = None

    @classmethod
    def get_local_dir(cls) -> Path:
        if cls.LOCAL_DIR is not None:
            return cls.LOCAL_DIR
        return Path.home() / ".atbclone" / "recipes"

    @classmethod
    def match(cls, bundle_id: str) -> Recipe:
        local_dir = cls.get_local_dir()
        local_file = local_dir / f"{bundle_id}.yaml"
        builtin_file = cls.BUILTIN_DIR / f"{bundle_id}.yaml"

        if local_file.is_file():
            return cls._load_file(local_file)
        if builtin_file.is_file():
            return cls._load_file(builtin_file)

        return Recipe(
            bundle_id=bundle_id,
            app_name="Unknown",
            strategy="hard_clone",
        )

    @staticmethod
    def _load_file(path: Path) -> Recipe:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return Recipe(**data)
