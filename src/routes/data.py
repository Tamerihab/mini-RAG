from fastapi import FastAPI, APIRouter, Depends, UploadFile
import os
from helpers.config import get_settings, Settings
from controllers import DataController

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}")
async def upload_data(
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):  
    data_controller = DataController()
    validation_result = await data_controller.validate_file(file)
    return validation_result
    