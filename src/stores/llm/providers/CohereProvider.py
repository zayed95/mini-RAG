from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnum, DocumentTypeEnum
import cohere
import logging

class CohereProvider(LLMInterface):

    def __init__(self, api_key: str, max_input_characters: int=1000,
                 max_output_tokens: int=1000, temperature: float=0.1):
        
        self.api_key = api_key

        self.default_max_input_characters = max_input_characters
        self.default_max_output_tokens = max_output_tokens
        self.default_temperature = temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.ClientV2(
            api_key=self.api_key
        )
        self.enums = CohereEnum
        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_max_input_characters].strip()

    def generate_text(self, prompt: str, chat_history: list=[],  
                      max_output_tokens: int=None, temperature: float = None):
        
        if not self.client:
            self.logger.error("CoHere client is not set!")
            return None
        
        if not self.generation_model_id:
            self.logger.error("CoHere generation model is not set!")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_max_output_tokens
        temperature = temperature if temperature else self.default_temperature

        response = self.client.chat(
            model=self.generation_model_id,
            messages=self.process_text(text=prompt),
            #chat_history=chat_history,
            temperature=temperature,
            max_tokens=max_output_tokens
        )

        if not response or not response.text:
            self.logger.error("Error generating text with CoHere")
            return None
        
        return response.text
    
    def embed_text(self, text = None, document_type = None):
        if not self.client:
            self.logger.error("CoHere client is not set!")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("CoHere embedding model is not set!")
            return None
        
        input_type = CohereEnum.QUERY
        if document_type == DocumentTypeEnum.DOCUMENT:
            input_type = CohereEnum.DOCUMENT

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            input_type=input_type,
            embedding_types=['float']
        )

        if not response or not response.embeddings or not response.embeddings.float_:
            self.logger.error("Error while embedding with CoHere!")
            return None
        
        return response.embeddings.float_[0]


    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": CohereEnum.USER.value,
            "text": self.process_text(text=prompt)
        }