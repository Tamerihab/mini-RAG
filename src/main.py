from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from routes import base, data, nlp
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    app.db_engine = create_async_engine(postgres_conn)
    app.db_session = async_sessionmaker(
        bind=app.db_engine,
        expire_on_commit=False)

    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create(
        provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(
        model_id=settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(
        provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)

    # vector db client
    app.vectordb_client = vectordb_provider_factory.create(
        provider_name=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANGUAGE, default_language=settings.DEFAULT_LANGUAGE)

    yield
 
    await app.db_engine.dispose()
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
