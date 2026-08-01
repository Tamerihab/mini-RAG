from helpers.config import get_settings, Settings
from pathlib import Path
import random
import string


class BaseController:
    def __init__(self):

        self.app_settings: Settings = get_settings()
        self.base_path = Path(__file__).resolve().parents[1]
        self.files_dir = self.base_path / "assets" / "files"

        self.database_dir = self.base_path / "assets" / "database"

    def generate_random_string(self, length: int = 12) -> str:
        """Generates a random string of fixed length."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def get_database_path(self, db_name: str) -> str:
        """Returns the path to the database directory."""
        if not self.database_dir.exists():
            self.database_dir.mkdir(parents=True, exist_ok=True)
        return str(self.database_dir / db_name)
