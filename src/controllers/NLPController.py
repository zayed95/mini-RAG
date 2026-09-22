import collections
from .BaseController import BaseController
from models.db_schemas import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json


class NLPController(BaseController):

    def __init__(self, vectordb_client, embedding_client,
                  generation_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser = template_parser

    
    def create_collection_name(self, project_id: str):
        return (f"collection_{self.vectordb_client.default_vector_size}_{project_id}").strip()
    
    async def reset_vectordb_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)

        
    
    async def get_vector_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info =  await self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
                json.dumps(collection_info, default=lambda x: x.__dict__)
            )
    

    async def index_into_vector_db(self, project: Project, chunks: List[DataChunk], 
                             chunk_ids: List[int]):

        collection_name = self.create_collection_name(project_id=project.project_id)

        texts = [chunk.chunk_text for chunk in chunks]
        metadata = [chunk.chunk_metadata for chunk in chunks]
        vectors = self.embedding_client.embed_text(text=texts, document_type=DocumentTypeEnum.DOCUMENT.value)

        does_collection_exists = await self.vectordb_client.does_collection_exist(collection_name=collection_name)
        if not does_collection_exists:
            _ = await self.vectordb_client.create_collection(
                collection_name=collection_name,
                embedding_size=self.embedding_client.embedding_size,
                
            )

        _ = await self.vectordb_client.insert_many(
            collection_name=collection_name,
            record_ids=chunk_ids,
            texts=texts,
            metadata=metadata,
            vectors=vectors
        )
        
        return True
    

    async def search_vectordb_collection(self, project: Project, text: str, limit: int = 5):

        collection_name = self.create_collection_name(project_id=project.project_id)

        query_vector = None 
        vectors = self.embedding_client.embed_text(
            text=text,
            document_type=DocumentTypeEnum.QUERY.value
        )

        if not vectors or len(vectors) == 0:
            return False

        if isinstance(vectors, list) and len(vectors) > 0:
            query_vector = vectors[0]

        if not query_vector:
            return False
        
        results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=query_vector,
            limit=limit
        )

        if not results:
            False

        return results
    
    async def answer_rag_question(self, project: Project, query: str, limit: int = 5):

        answer, full_prompt, chat_history = None, None, None

        retrieved_documents = await self.search_vectordb_collection(
            project=project,
            text=query,
            limit=limit
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return None, None, None
        
        system_prompt = self.template_parser.get("rag", "system_prompt")

        document_prompt = "/n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_num": idx+1,
                "chunk_text": self.generation_client.process_text(document.text)
            })
            for idx, document in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "system_prompt", {"query": query})

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value
            )
        ]

        full_prompt = "/n/n".join([document_prompt, footer_prompt])

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history