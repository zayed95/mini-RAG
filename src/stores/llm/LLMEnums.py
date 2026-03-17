from enum import Enum

class LLMEnum(Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    COHERE = "COHERE"

class OpenAIEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class CohereEnum(Enum):
    USER = "USER"
    CHATBOT = "CHATBOT"
    SYSTEM = "SYSTEM"

    DOCUMENT = "search_document"
    QUERY = "search_query"

class AnthropicEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class DocumentTypeEnum(Enum):
    DOCUMENT = "document"
    QUERY = "query"