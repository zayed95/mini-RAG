from email.policy import HTTP
from importlib.resources import contents

from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from routes.schemas.nlp import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers.NLPController import NLPController
from models import ResponseSignal
import logging

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/nlp",
    tags=["api", "nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):

    project_model = await ProjectModel(db_client=request.app.db_client).create_instance(db_client=request.app.db_client)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_or_create_project(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    
    nlp_controller = NLPController(
                                    vectordb_client=request.app.vectordb_client,
                                   embedding_client=request.app.embedding_client,
                                   generation_client=request.app.generation_client,
                                   template_parser=request.app.template_parser
                                   )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_no=page_no)

        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunk_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            do_reset=push_request.do_reset,
            chunk_ids=chunk_ids
        )

        if not is_inserted:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.INSERT_INTO_VECTOR_DB_ERROR.value
            }
        )

        inserted_items_count += len(page_chunks)
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTOR_DB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):

    project_model = await ProjectModel(
        db_client=request.app.db_client
        ).create_instance(db_client=request.app.db_client)
    
    project = await project_model.get_or_create_project(project_id=project_id)


    nlp_controller = NLPController(
                                    vectordb_client=request.app.vectordb_client,
                                   embedding_client=request.app.embedding_client,
                                   generation_client=request.app.generation_client
                                   )
    
    collection_info = nlp_controller.get_vector_collection_info(project=project)
    # print(collection_info)
    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info 
        }
    ) 

@nlp_router.post("/index/search/{project_id}")
async def search(request: Request, search_request: SearchRequest, project_id: str):

    project_model = await ProjectModel(
        db_client=request.app.db_client
        ).create_instance(db_client=request.app.db_client)
    
    project = await project_model.get_or_create_project(project_id=project_id)


    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                   embedding_client=request.app.embedding_client,
                                   generation_client=request.app.generation_client)
    
    results = nlp_controller.search_vectordb_collection(
        project=project,
        text=search_request.text,
        limit=search_request.limit
    )

    if not results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value
            }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results": results
        }
    )

@nlp_router.post("/index/answer/{project_id}")
async def answer(request: Request, search_request: SearchRequest, project_id: str):

    project_model = await ProjectModel(
        db_client=request.app.db_client
        ).create_instance(db_client=request.app.db_client)
    
    project = await project_model.get_or_create_project(project_id=project_id)


    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                   embedding_client=request.app.embedding_client,
                                   generation_client=request.app.generation_client)
    
    answer, full_prompt, chat_history = nlp_controller.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit
    )

    if not answer:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.RAG_ANSWER_ERROR.value
                }
            )      
    return JSONResponse(
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
            }
        )   
