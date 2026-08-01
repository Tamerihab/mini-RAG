import logging
import cohere
from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnums


class CoHereProvider(LLMInterface):

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

        self.client = cohere.ClientV2(
            api_key=self.api_key,
        )

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        self.logger.info(f"Set generation model to {model_id}")

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self.logger.info(
            f"Set embedding model to {model_id} with size {embedding_size}")

    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_characters].strip()

    def generate_text(
            self, prompt: str,
            chat_history: list = [],
            max_output_tokens: int = None,
            temperature: float = None
    ) -> str:

        if not self.client:
            self.logger.error("Cohere client not initialized")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        try:
            response = self.client.chat(
                model=self.generation_model_id,
                chat_history=chat_history,
                message=self.process_text(prompt),
                temperature=temperature,
                max_tokens=max_output_tokens

            )
            if not response or not response.text:
                self.logger.error("No response from Cohere API")
                return None
            return response.text.strip()

        except Exception as e:
            self.logger.error(f"Error generating text: {e}")
            return None

    def embed_text(self, text: str, document_type: str = None) -> list:
        if not self.client:
            self.logger.error("Cohere client not initialized")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model not set")
            return None

        input_type = CoHereEnums.DOCUMENT
        if document_type == DocumentTypeEnums.QUERY:
            input_type = CoHereEnums.QUERY

        try:
            response = self.client.embed(
                model=self.embedding_model_id,
                texts =[self.process_text(text)],
                input_type=input_type,
                embedding_types = ['float']
            )
            if not response or getattr(response, 'embeddings', None) is None or not response.embeddings.float:
                self.logger.error("No embeddings returned from Cohere API")
                return None
            return response.embeddings.float[0]

        except Exception as e:
            self.logger.error(f"Error embedding text: {e}")
            return None

    def construct_prompt(self, prompt: str, role: str) -> str:
        return {
            "role": role,
            "text": self.process_text(prompt)
        }
