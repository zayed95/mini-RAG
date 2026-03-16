from fastapi import FastAPI
from routes import BaseRouter, DataRouter
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMFactory import LLMFactory

app = FastAPI()


@app.on_event("startup")
async def start_db_client():

    settings = get_settings()
    llm_factory = LLMFactory(settings)

    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    app.generation_client = llm_factory.create(provider=settings.GENERATION_BACKENED)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    app.embedding_backend = llm_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_backend.set_embedding_model(model_id=settings.EMBEDDING_BACKEND,
                                              embedding_size=settings.EMBEDDING_MODEL_SIZE)


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()

    
app.include_router(BaseRouter.base_router)
app.include_router(DataRouter.data_router)
