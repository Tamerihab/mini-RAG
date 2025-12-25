from fastapi import UploadFile
from pathlib import Path
from .BaseController import BaseController
from models import ResponseSignal

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    
    def get_project_path(self, project_id: str) -> str:
        """
        Constructs the file path for a given project ID.
        Args:
            project_id (str): The unique identifier for the project. 
        Returns:
            str: The constructed file path for the project.
        """
        project_dir = self.files_dir / project_id

        if not project_dir.exists():
            project_dir.mkdir(parents=True, exist_ok=True)

        return project_dir