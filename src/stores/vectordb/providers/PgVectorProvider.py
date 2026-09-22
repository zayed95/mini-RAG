from stores.vectordb.VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import PgVectorTableEnums, PgVectorIndexTypeEnums
from models.db_schemas import RetrievedDocument
from typing import List
import logging
from sqlalchemy.sql import text as sql_text
import json

class PgVectorProvider(VectorDBInterface):

    def __init__(self, db_client, distance_method: str = None ,
                default_vector_size: int = 784, index_threshold: int = 100):
        
        self.db_client = db_client
        self.distance_method = distance_method
        self.default_vector_size = default_vector_size
        self.index_threshold = index_threshold

        self.pgvector_table_prefix = PgVectorTableEnums._PREFIX.value
        self.default_index_name = lambda collection_name: f"{collection_name}_vector_idx"

        self.logger = logging.getLogger("uvicorn")
    
    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text(
                    "CREATE EXTENSION IF NOT EXISTS vector"
                ))
                await session.commit()

    async def disconnect(self):
        pass

    async def does_collection_exist(self, collection_name):
        record = None
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text('SELECT * FROM pg_tables WHERE tablename = :collection_name')
                results = await session.execute(list_tbl, {"collections_name": collection_name})
                record = results.scalar_one_or_none()
        return record

    async def list_all_collections(self):
        records = []
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text("SELECT * FROM pg_tables WHERE tablename LIKE :prefix")
                results = await session.execute(list_tbl, {"prefix": self.pgvector_table_prefix})
                records = results.scalars().all()
        return records

    async def get_collection_info(self, collection_name):
        async with self.db_client() as session:
            async with session.begin():
                table_info_sql = sql_text('''
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes
                    FROM pg_tables WHERE tablename = :collection_name
                    ''')
                count_sql = sql_text('SELECT COUNT(*) FROM :collection_name')

                table_info = await session.execute(table_info_sql, {"collection_name": collection_name})
                record_count = await session.execute(count_sql, {"collection_name": collection_name})

                table_data = table_info.fetchone()
                if not table_data:
                    return None

                return {
                    "table_info": dict(table_data),
                    "record_count": record_count
                }
            
    async def delete_collection(self, collection_name):
        async with self.db_client() as session:
            async with session.begin():
                self.logger.info(f"Deleting collection: {collection_name}")
                delete_sql = sql_text('DELETE TABLE IF EXISTS :collection_name')
                await session.execute(delete_sql, {"collection_name": collection_name})
                await session.commit()
        return True

    async def create_collection(self, collection_name, embedding_size, do_reset):
        if do_reset:
            _ = await self.delete_collection(collection_name=collection_name)
        does_collection_exist = self.does_collection_exist(collection_name=collection_name)
        if not does_collection_exist:
            self.logger.info(f"Creating collection: {collection_name}")
            async with self.db_client() as session:
                async with session.begin():
                    create_sql = sql_text(
                        f'CREATE TABLE {collection_name} ('
                            f'{PgVectorTableEnums.ID.value} bigserial PRIMARY KEY,'
                            f'{PgVectorTableEnums.TEXT.value} text, '
                            f'{PgVectorTableEnums.VECTOR.value} vector({embedding_size}), '
                            f'{PgVectorTableEnums.METADATA.value} jsonb DEFAULT \'{{}}\', '
                            f'{PgVectorTableEnums.CHUNK_ID.value} integer, '
                            f'FOREIGN KEY ({PgVectorTableEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id)'
                        ')'
                    )

                    await session.execute(create_sql, {"collection_name": collection_name})
                    await session.commit()

            return True
        return False

    async def does_index_exist(self, collection_name: str):
            index_name = self.default_index_name(collection_name)
            async with self.db_client() as session:
                async with session.begin():
                    check_sql = sql_text(""" 
                                        SELECT 1
                                        FROM pg_indexes
                                        WHERE tablename = :collection_name
                                        AND indexname = :index_name""")
                    result = await session.execute(check_sql, {"collection_name": collection_name, "index_name": index_name})
                    return bool(result.scalar_one_or_none())

    async def create_index(self, collection_name: str, index_type: str = PgVectorIndexTypeEnums.HNSW.value):
        index_exists = self.does_index_exist(collection_name)
        if index_exists:
            return False

        async with self.db_client() as session:
            async with session.begin():
                count_sql = sql_text(f"SELECT COUNT(*) FROM f{collection_name}")
                result = await session.execute(count_sql)
                record_count = result.scalar_one()

                if record_count < self.index_threshold:
                    return False

                self.logger.info(f"Creating indexes over collection: {collection_name}")

                index_name = self.default_index_name(collection_name)
                create_idx_sql = sql_text(f'CREATE INDEX {index_name} ON {collection_name} '
                                          f'USING {index_type} ({PgVectorTableEnums.VECTOR.value} {self.distance_method})')
                await session.execute(create_idx_sql)

                self.logger.info(f"Done reating indexes over collection: {collection_name}")

    async def reset_index(self, collection_name: str, index_type: str = PgVectorIndexTypeEnums.HNSW.value):
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                drop_sql = sql_text(f'DROP INDEX IF EXISTS {index_name}')
                await session.execute(drop_sql)

        return await self.create_index(
            collection_name=collection_name,
            index_type=index_type
        )
    
    async def insert_one(self, collection_name, text, vector, metadata = None, record_id = None):
        does_collection_exist = await self.does_collection_exist()
        if not does_collection_exist:
            self.logger.info(f"Cannot insert a new record to nonexistent collection: {collection_name}")
            return False

        if not record_id:
            self.logger.info(f"Cannot insert a new record without chunk_id: {collection_name}")
            return False 
        
        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(f'INSERT INTO {collection_name} '
                                      f'({PgVectorTableEnums.TEXT.value}, {PgVectorTableEnums.VECTOR.value}, {PgVectorTableEnums.METADATA.value}, {PgVectorTableEnums.CHUNK_ID.value}) '
                                      'VALUES (:text, :vector, :metadata, :chunk_id)'
                                      )
                await session.execute(insert_sql, {
                    "text": text,
                    "vector": "[" + ", ".join([str(v) for v in vector]) + "]",
                    "metadata": metadata,
                    "chunk_id": record_id
                })
                await session.commit()
        return True
    
    async def insert_many(self, collection_name, texts, vectors, metadata, record_ids, batch_size = 50):
        does_collection_exist = await self.does_collection_exist()
        if not does_collection_exist:
            self.logger.info(f"Cannot insert a new record to nonexistent collection: {collection_name}")
            return False

        if len(vectors) != len(record_ids):
            self.logger.info(f"Invalid data items for collection: {collection_name}")
            return False

        if not metadata or len(metadata) == 0:
            metadata = [None] * len(texts)

        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i+batch_size]
                    batch_vectors = vectors[i:i+batch_size]
                    batch_metadata = metadata[i:i+batch_size]
                    batch_record_ids = record_ids[i:i+batch_size]

                    values = []

                    for _text, _vector, _metadata, _record_id in zip(batch_texts, batch_vectors,
                                                                      batch_metadata, batch_record_ids):
                        values.append({
                            "text": _text,
                            "vector": "[" + ", ".join([str(v) for v in _vector]) + "]",
                            "metadata": _metadata,
                            "chunk_id": _record_id
                        })

                    batch_insert_sql = sql_text(f'INSERT INTO {collection_name} '
                                      f'({PgVectorTableEnums.TEXT.value}, '
                                      f'{PgVectorTableEnums.VECTOR.value}, '
                                      f'{PgVectorTableEnums.METADATA.value}, '
                                      f'{PgVectorTableEnums.CHUNK_ID.value}) '
                                      f'VALUES (:text, :vector, :metadata, :chunk_id)')

                    await session.execute(batch_insert_sql)
                    await session.commit()
            return True
        
    async def search_by_vector(self, collection_name, vector, limit):
        does_collection_exist = await self.does_collection_exist()
        if not does_collection_exist:
            self.logger.info(f"Collection does not exist: {collection_name}")
            return False

        vector = "[" + ", ".join([str(v) for v in vector]) + "]"

        async with self.db_client() as session:
            async with session.begin():


                search_sql = sql_text(f'''SELECT {PgVectorTableEnums.TEXT.value} as text, 1 - ({PgVectorTableEnums.VECTOR.value} <=> :vector) as score 
                                    FROM {collection_name} 
                                    ORDER BY score DESC
                                    LIMIT {limit}''')
                result = await session.execute(search_sql, {"vector": vector})
                records = result.fetchall()

                return [RetrievedDocument(text=record.text, score=record.score)
                        for record in records]