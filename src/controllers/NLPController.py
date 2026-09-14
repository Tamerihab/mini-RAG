from stores.llm.templates.locales.en import rag

from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from typing import List
from stores.llm.LLMEnums import DocumentTypeEnums
import json


class NLPController(BaseController):

    def __init__(self, vectordb_client, generation_client, embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str) -> str:
        return f"collection_{project_id}".strip()

    def reset_vectordb_collection(self, project: Project):
        collection_name = self.create_collection_name(
            project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vectordb_collection_info(self, project: Project):
        collection_name = self.create_collection_name(
            project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(
            collection_name=collection_name)
        return json.loads(
            json.dumps(
                collection_info, default=lambda x: x.__dict__
            )
        )

    def index_into_vectordb(self, project: Project, data_chunks: List[DataChunk], chunks_ids: List[int], do_reset: bool = False):

        # 1- get collection name
        collection_name = self.create_collection_name(
            project_id=project.project_id)

        # 2- manage items
        texts = [c.chunk_text for c in data_chunks]
        metadatas = [c.chunk_metadata for c in data_chunks]

        vectors = [self.embedding_client.embed_text(
            text, document_type=DocumentTypeEnums.DOCUMENT.value) for text in texts]

        # 3- create collection if not exists

        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,

        )

        # 4- insert items into vector db

        self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            embedding_vectors=vectors,
            metadatas=metadatas,
            record_ids=chunks_ids
        )

        return True

    def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):

        # 1- get collection name
        collection_name = self.create_collection_name(
            project_id=project.project_id)

        # 2- get the text embedding vector
        vector = self.embedding_client.embed_text(
            text=text, document_type=DocumentTypeEnums.QUERY.value)

        if not vector or len(vector) == 0:
            self.logger.error(
                "Failed to generate embedding vector for the search text.")
            return False

        # 3- search in vector db
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

        if not results or len(results) == 0:
            self.logger.error(
                "No results found in the vector database for the given query.")
            return False

        return results


    def answer_rag_question(self, project: Project, query: str, limit: int = 10):

        answer,full_prompt, chat_history = None, None, None

        # 1 - retrieve relevant documents from vector db
        retrieved_documents = self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            self.logger.error(
                "No relevant documents found in the vector database for the given query.")
            return answer, full_prompt, chat_history

        # 2- Construct the prompt for the LLM
        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_num": idx + 1,
                "chunk_text": doc.text
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "query": query
        })

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt, role=self.generation_client.enums.SYSTEM.value)
        ]

        full_prompt = "\n\\n".join([
            documents_prompts,
            footer_prompt
        ])

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )   

        return answer, full_prompt, chat_history