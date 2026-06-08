import logging
from openai import OpenAI
from ..LLMInterface import LLMInterface
from ..LLMEnums import DeepSeekEnums


class DeepSeekProvider(LLMInterface):
    def __init__(
            self,
            api_key: str,
            default_input_max_characters: int = 1000,
            default_generation_max_tokens: int = 1000,
            default_generation_temperature: float = 0.1,
    ):
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_tokens = default_generation_max_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url
        )

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        self.logger.info(f"Set generation model to {model_id}")

    def set_embedding_model(self, model_id: str, embedding_size: int):
        raise NotImplementedError(
            "Deepseek does not support separate embedding models or embedding size configuration")

    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_characters].strip()

    def generate_text(
            self, prompt: str,
            chat_history: list = [],
            max_output_tokens: int = None,
            temperature: float = None
    ) -> str:

        if not self.client:
            self.logger.error("OpenAI client not initialized")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(prompt, DeepSeekEnums.USER.value)
        )

        try:
            reposnse = self.client.chat.completions.create(
                model=self.generation_model_id,
                stream=True,
                messages=chat_history,
                max_tokens=max_output_tokens,
                temperature=temperature,
            )
            if not reposnse or not reposnse.choices or len(reposnse.choices) == 0 or not reposnse.choices[0].message or not reposnse.choices[0].message.content:
                self.logger.error("Invalid response from DeepSeek API")
                return None
            return reposnse.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error while generating text: {str(e)}")
            return None
    def embed_text(self, text: str) -> list:
        raise NotImplementedError("Deepseek does not support separate embedding models or embedding size configuration")

    def construct_prompt(self,
                         prompt: str,
                         role: str
                         ) -> str:
        return {
            "role": role,
            "content": prompt.self.process_text(prompt)
        }
