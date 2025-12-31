from fastapi import FastAPI, APIRouter, Depends, UploadFile
from helpers.config import get_settings, Settings
from controllers import DataController

data_router = APIRouter(
    prefix="/api/data",
    tags=['api', 'data']
)

@data_router.post("/upload/{project_id}")
async def upload(project_id: str, file: UploadFile, app_settings: Settings=Depends(get_settings)):
    is_valid = DataController().validate_file(file=file)

    return is_valid