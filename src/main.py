from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from routes import base, data, nlp
#from motor.motor_asyncio import AsyncIOMotorClient # motor will be depercated so we will switch to pymongo instead 
from pymongo import AsyncMongoClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory


app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongodb_client = AsyncMongoClient(settings.MONGODB_URI)
    app.mongodb = app.mongodb_client[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)

    #vector db client
    app.vectordb_client = vectordb_provider_factory.create(provider_name=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    yield 

    await app.mongodb_client.close()
    await app.vectordb_client.disconnect()

# async def shutdown_span():
#    await app.mongodb_client.close()
#    await app.vectordb_client.disconnect()

# app.router.lifespan.on_startup.append(startup_span)
# app.router.lifespan.on_shutdown.append(shutdown_span)
app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
 
app.include_router(data.data_router)

app.include_router(nlp.nlp_router)

