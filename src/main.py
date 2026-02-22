from fastapi import FastAPI
from routes import BaseRouter, DataRouter

app = FastAPI()

app.include_router(BaseRouter.base_router)
app.include_router(DataRouter.data_router)
