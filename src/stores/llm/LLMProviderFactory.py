from .LLMEnums import LLMEnums
from .providers import CoHereProvider, OpenAIProvider, DeepSeekProvider

class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self,provider:str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key=self.config.get("OPENAI_API_KEY"),
                api_url=self.config.get("OPENAI_API_URL"),
                default_input_max_characters=self.config.get("INPUT_DEFAULT_MAX_CHARACTERS"),
                default_generation_max_tokens=self.config.get("GENERATION_DEFAULT_MAX_TOKENS"),
                default_generation_temperature=self.config.get("GENERATION_DEFAULT_TEMPERATURE"),
            )

        if provider == LLMEnums.COHERE.value:
            return CoHereProvider(
                api_key=self.config.get("COHERE_API_KEY"),
                default_input_max_characters=self.config.get("INPUT_DEFAULT_MAX_CHARACTERS"),
                default_generation_max_tokens=self.config.get("GENERATION_DEFAULT_MAX_TOKENS"),
                default_generation_temperature=self.config.get("GENERATION_DEFAULT_TEMPERATURE"),
            )

        if provider == LLMEnums.DEEPSEEK.value:
            pass # TODO: Implement DeepSeekProvider and return instance here

        return None
