from fastapi import FastAPI
from routes import BaseRouter, DataRouter, NLPRouter
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores import vectordb
from stores.llm.LLMFactory import LLMFactory
from stores.vectordb.VectorDBFactory import VectorDBFactory
from stores.llm.templates.template_parser import TemplateParser

app = FastAPI()


@app.on_event("startup")
async def start_db_client():

    settings = get_settings()
    llm_factory = LLMFactory(settings)
    vectordb_factory = VectorDBFactory(settings)

    # Connecting to mongodb
    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    # Setting the generation client
    app.generation_client = llm_factory.create(provider=settings.GENERATION_BACKENED)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Setting the embedding client
    app.embedding_client = llm_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                              embedding_size=settings.EMBEDDING_MODEL_SIZE)

    # Setting the vectordb client
    app.vectordb_client = vectordb_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        def_language=settings.DEFAULT_LANG
        )

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()

    app.vectordb_client.disconnect()

    
app.include_router(BaseRouter.base_router)
app.include_router(DataRouter.data_router)
app.include_router(NLPRouter.nlp_router)

