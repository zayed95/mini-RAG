from models.db_schemas.minirag.schema import Project
from models.
from .BaseDataModel import BaseDataModel
from .db_schemas import Asset
from .enums.DatabaseEnum import DatabaseEnum
from bson.objectid import ObjectId
from sqlalchemy import select

class AssetModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client
    
    # A method to create an instance of the class and initiate a collection for it in the database
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    
    # A function to insert an asset into the database
    async def create_asset(self, asset: Asset):
        async with self.db_client() as session:
            async with session.begin():
                await session.add(asset)
            await session.commit()
            await session.refresh(asset)  
        return asset
    
    # A function to return all assets of a certain type in the database as pydantic model
    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        async with self.db_client() as session:
            async with session.begin():
                query = session.select(Project).where(Project.project_id == asset_project_id)
                project_rec = query.scalar_one_or_none()
                if project_rec is None:
                    self.cr
    
    async def get_asset_record(self, asset_project_id: str, asset_name: str):

        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id),
            "asset_name": asset_name
        })

        if record:
            return Asset(**record)

        return None