from enum import Enum


class LLMEnums(Enum):

    OPENAI = "OPENAI"
    DEEPSEEK = "DEEPSEEK"
    COHERE = "COHERE"

class OpenAIEnums(Enum):

    SYSTEM = "system"
    USER = "user"       
    ASSISTANT = "assistant"

class CoHereEnums(Enum):

    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"
    DOCUMENT = "search_document"
    QUERY = "search_query"

class DeepSeekEnums(Enum):
    
    SYSTEM = "system"
    USER = "user"
class DocumentTypeEnums(Enum):

    DOCUMENT = "document"
    QUERY = "query"