from fastapi import FastAPI
from routes import base, data
#from motor.motor_asyncio import AsyncIOMotorClient # motor will be depercated so we will switch to pymongo instead 
from pymongo import AsyncMongoClient
from helpers.config import get_settings


app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongodb_client = AsyncMongoClient(settings.MONGODB_URI)
    app.mongodb = app.mongodb_client[settings.MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown_db_client():
   await app.mongodb_client.close()

app.include_router(base.base_router)
 
app.include_router(data.data_router)

