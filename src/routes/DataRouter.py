import os, aiofiles, logging
from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from .schemas.data import ProcessRequest
from models.db_schemas import DataChunk, Asset
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models import ResponseSignal
from models.enums.AssetTypeEnum import AssetTypeEnum

# Create logger tp get the uvicorn logs for monitoring the app
logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/data",
    tags=['api', 'data']
)


# The first endpoint to upload a file
@data_router.post("/upload/{project_id}")
async def upload(request: Request, project_id: str, file: UploadFile, app_settings: Settings=Depends(get_settings)):

    # The following 2 lines get the project from the database or create the project if it doesn't exist
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)

    # Initiate an instance of the DataController to take advantage of its validation function
    data_controller = DataController()
    is_valid, response_signal = data_controller.validate_file(file=file)

    if not is_valid:

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': response_signal}
        )
    
    project_dir_path = ProjectController().get_project_directory(project_id)

    file_path, file_id = data_controller.generate_unique_file_path(
        original_filename=file.filename, 
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, 'wb') as f:

            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:

        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.FILE_UPLOAD_FAILED.value}
        )
    
    # Save the file as an asset in the database
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.ASSET_TYPE_FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path)
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)
    
    return JSONResponse(
            content={
                'signal': ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset_record.asset_name)
                }
        )

# The second endpoint to process a request
@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):

    # 
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    chunk_overlap = process_request.chunk_overlap
    do_reset = process_request.do_reset

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)

    

    process_controller = ProcessController(project_id=project_id)

    file_content = process_controller.get_file_content(file_id=file_id)

    file_chunks = process_controller.process_file_content(
        file_id=file_id,
        file_content=file_content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal': ResponseSignal.PROCESSING_FAIL.value}
        )
    
    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.id
        )

        for i, chunk in enumerate(file_chunks)
    ]

    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)


    chunk_num = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "inserted_chunks": chunk_num 
            }
        )




