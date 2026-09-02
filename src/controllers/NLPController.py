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
        return (f"collection_{project_id}").strip()
    
    def reset_vectordb_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

        
    
    def get_vector_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info =  self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
                json.dumps(collection_info, default=lambda x: x.__dict__)
            )
    

    def index_into_vector_db(self, project: Project, chunks: List[DataChunk], 
                             chunk_ids: List[int], do_reset: bool=False):

        collection_name = self.create_collection_name(project_id=project.project_id)

        texts = [chunk.chunk_text for chunk in chunks]
        metadata = [chunk.chunk_metadata for chunk in chunks]

        vectors = [
            self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]

        if not self.vectordb_client.does_collection_exist(collection_name=collection_name):
            _ = self.vectordb_client.create_collection(
                collection_name=collection_name,
                embedding_size=self.embedding_client.embedding_size,
                do_reset=do_reset
            )

        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            record_ids=chunk_ids,
            texts=texts,
            metadata=metadata,
            vectors=vectors
        )
        
        return True
    

    def search_vectordb_collection(self, project: Project, text: str, limit: int = 5):

        collection_name = self.create_collection_name(project_id=project.project_id)

        vector = self.embedding_client.embed_text(
            text=text,
            document_type=DocumentTypeEnum.QUERY.value
        )

        if not vector or len(vector) == 0:
            return False
        
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        if not results:
            False

        return results
    
    def answer_rag_question(self, project: Project, query: str, limit: int = 5):

        answer, full_prompt, chat_history = None, None, None

        retrieved_documents = self.search_vectordb_collection(
            project=project,
            text=query,
            limit=limit
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return None, None, None
        
        system_prompt = self.template_parser.get("rag", "system_prompt")

        document_prompt = "/n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_number": idx+1,
                "chunk_text": document.text
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