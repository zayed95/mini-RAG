from .LLMEnums import LLMEnum
from .providers import CohereProvider, AnthropicProvider, OpenAIProvider

class LLMFactory():

    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):

        if provider == LLMEnum.ANTHROPIC.value:
            return AnthropicProvider(
                api_key=self.config.ANTHROPC_API_KEY,
                max_input_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        if provider == LLMEnum.COHERE.value:
            return CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                max_input_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        return None