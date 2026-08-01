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
    NO_FILES_TO_PROCESS = "No files to process."
    FILE_ID_ERROR = "Provided file_id does not exist in the project."
    PROJECT_NOT_FOUND = "Project not found."
    INSERT_INTO_VECTOR_DB_ERROR = "Failed to insert data chunks into vector database."
    INSERT_INTO_VECTOR_DB_SUCCESS = "Data chunks successfully inserted into vector database."
    COLLECTION_INFO_RETRIEVED = "Collection information retrieved successfully."
    COLLECTION_NOT_FOUND = "Collection not found in vector database."
    VECTOR_DB_SEARCH_ERROR = "Failed to search in vector database."
    VECTOR_DB_SEARCH_SUCCESS = "Search in vector database completed successfully."

