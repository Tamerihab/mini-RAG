from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum


class ProjectModel(BaseDataModel):
    def __init__(self, mongodb_client: object):
        super().__init__(mongodb_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    async def create_project(self, project: Project) -> str:
        result = await self.collection.insert_one(project.dict())
        project._id = result.inserted_id
        return project

    async def get_project_or_create_one(self, project_id: str):

        record = await self.collection.find_one({
            "project_id": project_id
        })

        if record is None:

            project = Project(project_id=project_id)
            return await self.create_project(project=project)

        return Project(**record)

    async def get_all_projects(self, page: int = 1, page_size: int = 10):

        total_documents = await self.collection.count_documents({})
        total_pages = (total_documents + page_size - 1) // page_size

        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(Project(**document))
        return projects, total_pages
