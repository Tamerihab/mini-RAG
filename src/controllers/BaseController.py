from helpers.config import get_settings, Settings
from pathlib import Path
import random 
import string
class BaseController:
    def __init__(self):
        
        self.app_settings: Settings = get_settings()
        self.base_path = Path(__file__).resolve().parents[1]
        self.files_dir = self.base_path / "assets" / "files"

    def generate_random_string(self,length: int = 12) -> str:
        """Generates a random string of fixed length."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    