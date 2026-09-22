from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodsEnum
from models.db_schemas import RetrievedDocument
from typing import List
import logging

class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_client: str, distance_method: str = None ,
                default_vector_size: int = 784, index_threshold: int = 100):

        self.db_client = db_client
        self.distance_method = None
        self.client = None
        self.default_vector_size = default_vector_size
        self.index_threshold = index_threshold

        if distance_method == DistanceMethodsEnum.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodsEnum.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger("uvicorn")

    async def connect(self):
        self.client = QdrantClient(path=self.db_client)

    async def disconnect(self):
        self.client = None

    async def does_collection_exist(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    async def list_all_collections(self) -> List:
        return self.client.get_collections()

    async def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    async def delete_collection(self, collection_name: str) -> None:
        if self.does_collection_exist(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    async def create_collection(self, collection_name: str,
                          embedding_size: int,
                          do_reset: bool):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)

        if not self.does_collection_exist(collection_name=collection_name):
            self.logger.info(f"Creating a new Qdrant collection: {collection_name}")
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )

            return True
        
        return False
    

    async def insert_one(self, collection_name: str, text: str,
                   vector: list, metadata: dict=None, record_id: str=None):
        
        if not self.does_collection_exist(collection_name):
            self.logger.error(f"Cannot insert new record. Collection {collection_name} does not exist!")
            return None
        
        try:
            _ = self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=[record_id],
                        vector=vector,
                        payload={
                            "text": text, 
                            "metadata": metadata
                            }
                    )
                ]
            )
        
        except Exception as e:
            self.logger.error(f"Error while inserting record: {e}")
            return False

        return True


    async def insert_many(self, collection_name: str, texts: list, vectors: list, 
                    metadata: list, record_ids: list, batch_size: int=50):
        
        if not metadata:
            metadata = [None] * len(texts)
        
        if not record_ids:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            text_batch = texts[i:batch_end]
            metadata_batch = metadata[i:batch_end]
            vector_batch = vectors[i:batch_end]
            record_batch = record_ids[i:batch_end]

            record_batch = [
                models.PointStruct(
                    id=record_batch[x],
                    vector=vector_batch[x],
                    payload={
                        "text": text_batch[x], 
                        "metadata": metadata_batch[x]
                        }
                )

                for x in range(len(text_batch))
            ]

            try: 
                _ = self.client.upsert(
                collection_name=collection_name,
                points=record_batch
                )

            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

        return True


    async def search_by_vector(self, collection_name: str, vector: list, limit: int=5)  -> None | List[RetrievedDocument]:

        result = self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit
        )

        if not result:
            return None
        
        return [
            RetrievedDocument(**{
                "score": point.score,
                "text": point.payload["text"]
            })

            for point in result.points
        ]