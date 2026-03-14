from enum import Enum

class LLMEnum(Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    COHERE = "COHERE"

class OpenAIEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
