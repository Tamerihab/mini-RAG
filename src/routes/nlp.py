from fastapi import FastAPI, APIRouter, status, Request
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NLPController
from models import ResponseSignal
import logging


logger = logging.getLogger(__name__)

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)


@nlp_router.post("/index/push/{project_id}")
async def push_index(request: Request, project_id: str, push_request: PushRequest):

    project_model = await ProjectModel.create_instance(
        mongodb_client=request.app.mongodb
    )

    chunk_model = await ChunkModel.create_instance(
        mongodb_client=request.app.mongodb
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value,
                     "message": f"Project with id {project_id} not found."},
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    while has_records:
        page_chunks = await chunk_model.get_chunks_by_project_id(project_id=project.id, page_no=page_no)

        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunk_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = nlp_controller.index_into_vectordb(
            project=project,
            data_chunks=page_chunks,
            do_reset=push_request.do_reset,
            chunks_ids=chunk_ids
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"signal": ResponseSignal.INSERT_INTO_VECTOR_DB_ERROR.value,
                         "message": f"Failed to insert data chunks into vector database for project {project_id}."},
            )

        inserted_items_count += len(page_chunks)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"signal": ResponseSignal.INSERT_INTO_VECTOR_DB_SUCCESS.value,
                 "inserted_items_count": inserted_items_count,
                 "message": f"Data chunks for project {project_id} have been successfully inserted into vector database."
                 },
    )


@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):

    project_model = await ProjectModel.create_instance(
        mongodb_client=request.app.mongodb
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value,
                     "message": f"Project with id {project_id} not found."},
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
    )

    collection_info = nlp_controller.get_vectordb_collection_info(
        project=project)

    if not collection_info:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.COLLECTION_NOT_FOUND.value,
                     "message": f"Collection for project {project_id} not found in vector database."},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"signal": ResponseSignal.COLLECTION_INFO_RETRIEVED.value,
                 "collection_info": collection_info,
                 "message": f"Collection info for project {project_id} retrieved successfully."
                 },
    )


@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(
        mongodb_client=request.app.mongodb
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value,
                     "message": f"Project with id {project_id} not found."},
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
    )

    results = nlp_controller.search_vector_db_collection(
        project=project,
        text=search_request.text,
        limit=search_request.limit
    )

    if not results:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.VECTOR_DB_SEARCH_ERROR.value,
                     "message": f"No results found for the search query in project {project_id}."},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"signal": ResponseSignal.VECTOR_DB_SEARCH_SUCCESS.value,
                 "results": results,
                 "message": f"Search in vector database for project {project_id} completed successfully."
                 },
    )
