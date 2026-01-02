from fastapi import UploadFile
import os
from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ResponseSignal
import re


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # Size scale to convert bytes to megabytes

    async def validate_file(self, file: UploadFile) -> bool:

        # Validate file extension
        allowed_extensions = self.app_settings.FILE_ALLOWED_EXTENSIONS
        file_extension = os.path.splitext(file.filename)[1]
        if file_extension not in allowed_extensions:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        # Validate file size
        file_size_mb = len(await file.read()) / (self.size_scale)
        if file_size_mb > self.app_settings.FILE_MAX_SIZE_MB:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value

    def generate_unique_filepath(self, original_filename: str, project_id: str) -> str:

        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_filename = self.get_clean_filename(original_filename)

        new_file_path = project_path / (random_key + "_" + cleaned_filename)

        while new_file_path.exists():
            random_key = self.generate_random_string()
            new_file_path = project_path / (random_key + "_" + cleaned_filename)

        return new_file_path, random_key + "_" + cleaned_filename

    def get_clean_filename(self, filename: str) -> str:

        cleaned_filename = re.sub(r'[^\w.]', '', filename.strip())

        cleaned_filename = cleaned_filename.replace(' ', '_')

        return cleaned_filename
