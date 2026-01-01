from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController

data_router = APIRouter(
    prefix="/api/data",
    tags=['api', 'data']
)

@data_router.post("/upload/{project_id}")
async def upload(project_id: str, file: UploadFile, app_settings: Settings=Depends(get_settings)):
    is_valid, response_signal = DataController().validate_file(file=file)

    if not is_valid:

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': response_signal}
        )
    
    project_dir_path = ProjectController().get_project_dir(project_id)