from enum import Enum
import os
from helpers.config import get_settings


class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "File validated successfully."
    FILE_TYPE_NOT_SUPPORTED = "File type not supported."
    FILE_SIZE_EXCEEDED = "File size exceeded."
    FILE_UPLOAD_SUCCESS = "File uploaded successfully."
    FILE_UPLOAD_FAILED = "File upload failed."
    FILE_PROCESSING_SUCCESS = "File processing succeeded."  
    FILE_PROCESSING_FAILED = "File processing failed."
