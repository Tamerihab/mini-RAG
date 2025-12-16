from fastapi import UploadFile
import os
from .BaseController import BaseController


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # Size scale to convert bytes to megabytes

    async def validate_file(self, file: UploadFile) -> bool:

        # Validate file extension
        allowed_extensions = self.app_settings.FILE_ALLOWED_EXTENSIONS
        file_extension = os.path.splitext(file.filename)[1]
        if file_extension not in allowed_extensions:
            return False, f"File extension '{file_extension}' is not allowed."

        # Validate file size
        file_size_mb = len(await file.read()) / (self.size_scale)
        if file_size_mb > self.app_settings.FILE_MAX_SIZE_MB:
            return False, f"File size {file_size_mb:.2f} MB exceeds the maximum allowed size of {self.app_settings.FILE_MAX_SIZE_MB} MB."

        return True
