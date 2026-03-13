from .BaseDataModel import BaseDataModel
from .db_schemas import Asset
from .enums.DatabaseEnum import DatabaseEnum
from bson.objectid import ObjectId

class AssetModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_ASSET_NAME.value]
    
    # A method to create an instance of the class and initiate a collection for it in the database
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    # A function to initiate a collection for the assetsin the database if one soesn;t exist already
    async def init_collection(self):

        old_collections = await self.db_client.list_collection_names()

        if DatabaseEnum.COLLECTION_ASSET_NAME not in old_collections:
            self.collection = self.db_client[DatabaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index['key'],
                    name=index['name'],
                    unique=index['unique']
                )
    
    # A function to insert an asset into the database
    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id

        return asset
    
    # A function to return all assets of a certain type in the database as pydantic model
    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):

        records = await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_type": asset_type 
        }).to_list(length=None)

        return [
            Asset(**record)
            for record in records
        ]
    
    async def get_asset_record(self, asset_project_id: str, asset_name: str):

        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id),
            "asset_name": asset_name
        })

        if record:
            return Asset(**record)

        return None