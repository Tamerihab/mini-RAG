from enum import Enum


class LLMEnums(Enum):

    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    COHERE = "cohere"

class OpenAIEnums(Enum):

    SYSTEM = "system"
    USER = "user"       
    ASSISTANT = "assistant"