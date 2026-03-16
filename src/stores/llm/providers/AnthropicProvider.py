from ..LLMInterface import LLMInterface
from ..LLMEnums import AnthropicEnum
from anthropic import Anthropic
import logging


class AnthropicProvider(LLMInterface):

    def __init__(self, api_key: str, max_input_characters: int=1000,
                 max_output_tokens: int=1000, temperature: float=0.1):
        
        self.api_key = api_key

        self.default_max_input_characters = max_input_characters
        self.default_max_output_tokens = max_output_tokens
        self. default_temperature = temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_model_size = None

        self.client = Anthropic(api_key=api_key)

        self.logger = logging.getLogger(__name__)

    
    def set_generation_model(self, model_id):
        self.generation_model_id = model_id
        return None
    
    def set_embedding_model(self, model_id, embedding_size):
        self.embedding_model_id = model_id
        self.embedding_model_size = embedding_size
        return None
    
    def process_text(self, text: str):
        return text[:self.default_max_input_characters].strip()
    
    def generate_text(self, prompt: str, chat_history: list=[],  
                      max_output_tokens: int=None, temperature: float = None):
        
        if not self.client:
            self.logger.error("Anthropic client is not set!")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Anthropic generation model is not set!")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_max_output_tokens
        temperature = temperature if temperature else self.default_temperature

        response = self.client.messages.create(
            max_tokens=max_output_tokens,
            messages=[self.construct_prompt(prompt=prompt, role=AnthropicEnum.USER.value)],
            model=self.generation_model_id
        )

        if not response or not response.content:
            self.logger.error("Error while generating text with Anthropic!")
            return None
        
        return response.content

    def embed_text(self, text: None, document_type: str=None):
        raise NotImplementedError
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }