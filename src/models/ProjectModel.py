from models.db_schemas.minirag.schema import project

from .BaseDataModel import BaseDataModel
from .db_schemas.project import Project
from .enums.DatabaseEnum import DatabaseEnum
from sqlalchemy import select, func

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    async def create_project(self, project: Project):
        async with self.db_client() as session:
            async with session.begin():
                await session.add(project)
            await session.commit()
            await session.refresh(project)    
        return project    

    async def get_or_create_project(self, project_id: str):
        async with self.db_client() as session:
            async with session.begin():
                query = await session.execute(select(Project).where(Project.project_id == project_id))
                project = query.scalar_one_or_none()
                if project is None:
                    project_rec = Project(project_id=project_id)
                    project = self.create_project(project_rec)
        return project
                


    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        async with self.db_client() as session:
            async with session.begin():
                total_documents = await session.execute(select(
                    func.count(Project.project_id)
                ))
                total_documents = total_documents.scalar_one_or_none()
                total_pages = total_documents // page_size
                if total_documents % page_size > 0:
                    total_pages += 1

                query = await session.execute(select(Project).offset((page - 1) * page_size).limit(page_size))
                projects = query.scalars().all()

        return projects, total_pages