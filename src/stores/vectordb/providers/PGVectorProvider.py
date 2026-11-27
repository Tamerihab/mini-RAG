from pymongo import collection

from ..VectorDBinterface import VectorDBInterface
from ..VectorDBEnums import (VectorDBEnums, DistanceMetricEnums,
                             PgVectorTableSchemeEnums, PgVectorDistanceMethodEnums, PgVectorIndexTypeEnums)

from models.db_schemes import RetrievedDocument
from typing import List
import logging
from sqlalchemy.sql import text as sql_text
import json


class PgVectorProvider(VectorDBInterface):

    def __init__(self, db_client, default_vector_size: int = 786,
                 distance_method: str = None):

        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.distance_method = distance_method

        self.pgvvector_table_prefix = PgVectorTableSchemeEnums._PREFIX.value

        self.logger = logging.getLogger("uvicorn")

    async def connect(self):

        async with self.db_client.begin() as session:
            async with session.begin():
                await session.execute(sql_text(
                    "CREATE EXTENSION IF NOT EXISTS vector;"
                ))
                await session.commit()

    async def disconnect(self):
        pass

    async def is_collection_exists(self, collection_name: str) -> bool:
        async with self.db_client.begin() as session:
            async with session.begin():
                list_tbl = sql_text(
                    "SELECT * FROM pg_tables WHERE tablename = :collection_name;")
                results = await session.execute(list_tbl, {"collection_name": collection_name})
                record = results.scalar_one_or_none()

        return record

    async def list_all_collections(self) -> List:
        records = []
        async with self.db_client.begin() as session:
            async with session.begin():
                list_tbl = sql_text(
                    "SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix;")
                results = await session.execute(list_tbl, {"prefix": f"{self.pgvvector_table_prefix}%"})
                records = results.scalar().all()

        return records

    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client.begin() as session:
            async with session.begin():
                get_tbl_info = sql_text(
                    "SELECT schemaname, tablename, tableowner, tablespace, hasindexes"
                    " FROM pg_tables WHERE tablename = :collection_name;")

                count_sql = sql_text(
                    "SELECT COUNT(*) FROM :collection_name")
                table_info = await session.execute(get_tbl_info, {"collection_name": collection_name})
                record_count = await session.execute(count_sql, {"collection_name": collection_name})

                table_data = table_info.fetchone()
                if not table_data:
                    return None

        return {
            "table_info": dict(table_data),
            "record_count": record_count.scalar()
        }

    async def delete_collection(self, collection_name: str):
        async with self.db_client.begin() as session:
            async with session.begin():
                self.logger.info(
                    f"Deleting collection '{collection_name}'...")
                delete_sql = sql_text(""
                                      "DROP TABLE IF EXISTS :collection_name;")
                await session.execute(delete_sql, {"collection_name": collection_name})
                await session.commit()

        return True

    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):

        if do_reset:
            _ = await self.delete_collection(collection_name=collection_name)

        is_collection_exists = await self.is_collection_exists(collection_name=collection_name)

        if not is_collection_exists:
            self.logger.info(
                f"Creating collection '{collection_name}' with embedding size {embedding_size}...")
            async with self.db_client.begin() as session:
                async with session.begin():
                    create_sql = sql_text(
                        f'CREATE TABLE {collection_name} ('
                        f'{PgVectorTableSchemeEnums.ID.value} bigserial PRIMARY KEY,'
                        f'{PgVectorTableSchemeEnums.VECTOR.value} vector(:embedding_size),'
                        f'{PgVectorTableSchemeEnums.TEXT.value} text,'
                        f'{PgVectorTableSchemeEnums.CHUNK_ID.value} integer,'
                        f'{PgVectorTableSchemeEnums.METADATA.value} jsonb DEFAULT \'{{}}\''
                        f'FOREIGN KEY ({PgVectorTableSchemeEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id)'
                        ')'
                    )
                    await session.execute(create_sql)
                    await session.commit()
            return True

        return False

    async def insert_one(self, collection_name: str,
                         text: str, embedding_vector: list, metadata: dict = None, record_id: str = None):

        is_collection_exists = await self.is_collection_exists(collection_name=collection_name)

        if not is_collection_exists:
            self.logger.error(
                f"Collection '{collection_name}' does not exist. Cannot insert record.")
            return False

        if not record_id:
            self.logger.error(
                f"Record ID is required for inserting a record into collection '{collection_name}'.")
            return False

        async with self.db_client.begin() as session:
            async with session.begin():
                insert_sql = sql_text(f'INSERT INTO {collection_name} '
                                      f'{PgVectorTableSchemeEnums.TEXT.value}, '
                                      f'{PgVectorTableSchemeEnums.VECTOR.value}, '
                                      f'{PgVectorTableSchemeEnums.METADATA.value}, '
                                      f'{PgVectorTableSchemeEnums.CHUNK_ID.value}) '
                                      f'VALUES (:text, :embedding_vector, :metadata, :chunk_id)')

                await session.execute(insert_sql, {
                    "text": text,
                    "embedding_vector": "[" + ",".join([str(v) for v in embedding_vector]) + "]",
                    "metadata": metadata,
                    "chunk_id": record_id
                })
                await session.commit()

        return True

    async def insert_many(self, collection_name: str,
                          texts: List[str], embedding_vectors: List[list],
                          metadatas: List[dict] = None, record_ids: List[str] = None,
                          batch_size: int = 50):

        is_collection_exists = await self.is_collection_exists(collection_name=collection_name)

        if not is_collection_exists:
            self.logger.error(
                f"Collection '{collection_name}' does not exist. Cannot insert records.")
            return False

        if not record_ids or len(record_ids) != len(texts):
            self.logger.error(
                f"Record IDs are required and must match the number of texts for inserting records into collection '{collection_name}'.")
            return False

        if not metadatas or len(metadatas) == 0:
            metadatas = [None] * len(texts)

        async with self.db_client.begin() as session:
            async with session.begin():
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    batch_vectors = embedding_vectors[i:i + batch_size]
                    batch_metadatas = metadatas[i:i + batch_size] if metadatas else [
                        None] * len(batch_texts)
                    batch_record_ids = record_ids[i:i + batch_size]

                    insert_sql = sql_text(f'INSERT INTO {collection_name} '
                                          f'({PgVectorTableSchemeEnums.TEXT.value}, '
                                          f'{PgVectorTableSchemeEnums.VECTOR.value}, '
                                          f'{PgVectorTableSchemeEnums.METADATA.value}, '
                                          f'{PgVectorTableSchemeEnums.CHUNK_ID.value}) '
                                          f'VALUES (:text, :embedding_vector, :metadata, :chunk_id)')

                    for text, vector, metadata, record_id in zip(batch_texts, batch_vectors, batch_metadatas, batch_record_ids):
                        await session.execute(insert_sql, {
                            "text": text,
                            "embedding_vector": "[" + ",".join([str(v) for v in vector]) + "]",
                            "metadata": metadata,
                            "chunk_id": record_id
                        })

                await session.commit()

        return True

    async def search_by_vector(self, collection_name, query_vector, top_k):

        is_collection_exists = await self.is_collection_exists(collection_name=collection_name)

        if not is_collection_exists:
            self.logger.error(
                f"Collection '{collection_name}' does not exist. Cannot search by vector.")
            return False

        vector = "[" + ",".join([str(v) for v in query_vector]) + "]"

        async with self.db_client() as session:
            async with session.begin():
                search_sql = sql_text(
                    f'SELECT {PgVectorTableSchemeEnums.TEXT.value} as text, 1 - ({PgVectorTableSchemeEnums.VECTOR.value} <=> :vector) as score'
                    f'FROM {collection_name} '
                    f'ORDER BY score DESC, {PgVectorTableSchemeEnums.VECTOR.value} <=> :vector LIMIT :top_k')
                
                results = await session.execute(search_sql, {"vector": vector, "top_k": top_k})

                records= results.fetchall()

                return [
                    RetrievedDocument(
                        text = record.text,
                        score = record.score
                    )
                    for record in records
                ]

            