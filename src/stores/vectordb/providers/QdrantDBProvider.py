from ..VectorDBinterface import VectorDBInterface
from ..VectorDBEnums import DistanceMetricEnums
from qdrant_client import QdrantClient, models
from typing import List
import logging
from models.db_schemes import RetrievedDocument


class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_path: str, distance_metric: str):

        self.client = None
        self.db_path = db_path
        self.distance_metric = None

        if distance_metric == DistanceMetricEnums.COSINE.value:
            self.distance_metric = models.Distance.COSINE
        elif distance_metric == DistanceMetricEnums.EUCLIDEAN.value:
            self.distance_metric = models.Distance.EUCLIDEAN
        elif distance_metric == DistanceMetricEnums.DOT.value:
            self.distance_metric = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        self.logger.info("Connected to Qdrant database.")

    def disconnect(self):
        self.client = None
        self.logger.info("Disconnected from Qdrant database.")

    def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self) -> List:
        collections = self.client.get_collections()
        return [collection.name for collection in collections.collections]

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):

        try:
            if self.is_collection_exists(collection_name=collection_name):
                self.client.delete_collection(collection_name=collection_name)
                self.logger.info(
                    f"Collection '{collection_name}' deleted successfully.")
            else:
                self.logger.warning(
                    f"Collection '{collection_name}' does not exist.")
        except Exception as e:
            self.logger.error(
                f"Error while deleting collection '{collection_name}': {e}")
            raise e

    def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        do_reset: bool = False
    ):

        try:
            if self.is_collection_exists(collection_name=collection_name):
                if do_reset:
                    self.delete_collection(collection_name=collection_name)
                else:
                    self.logger.warning(
                        f"Collection '{collection_name}' already exists.")
                    return

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_metric
                )
            )
            self.logger.info(
                f"Collection '{collection_name}' created successfully.")
        except Exception as e:
            self.logger.error(
                f"Error while creating collection '{collection_name}': {e}")
            raise e

    def insert_one(
        self,
        collection_name: str,
        text: str,
        embedding_vector: list,
        metadata: dict = None,
        record_id: str = None
    ):
        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.error(
                f"Collection '{collection_name}' does not exist. Cannot insert record.")
            raise ValueError(
                f"Collection '{collection_name}' does not exist. Cannot insert record.")
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=record_id,
                        vector=embedding_vector,
                        payload={"text": text, **(metadata or {})}
                    )
                ]
            )
        except Exception as e:
            self.logger.error(
                f"Error while inserting record into collection '{collection_name}': {e}")
            raise e

        return True

    def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        embedding_vectors: List[list],
        metadatas: List[dict] = None,
        record_ids: List[str] = None,
        batch_size: int = 50
    ):
        if metadatas is None:
            metadatas = [{}] * len(texts)

        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):

            batch_end = i + batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = embedding_vectors[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            # 1. Change models.Record to models.PointStruct
            batch_points = []
            for text, vector, metadata, record_id in zip(batch_texts, batch_vectors, batch_metadatas, batch_record_ids):
                if vector is None:
                    # Skip this point and log a warning instead of crashing
                    print(f"Warning: Skipping record {record_id} because its vector is None.")
                    continue
                    
                batch_points.append(
                    models.PointStruct(
                        id=record_id,
                        vector=vector,
                        payload={"text": text, **(metadata or {})}
                    )
                )

            # Only proceed if we actually have valid points to upload
            if not batch_points:
                continue
            try:
                # 2. Change records= to points=
                _ = self.client.upload_points(
                    collection_name=collection_name,
                    points=batch_points
                )
            except Exception as e:
                self.logger.error(
                    f"Error while inserting batch of records into collection '{collection_name}': {e}")
                raise e

        return True
    def search_by_vector(
        self,
        collection_name: str,
        query_vector: list,
        limit: int = 5,
    ):
        response = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
        )

        if not response or len(response.points) == 0:
            return None

        return [
            RetrievedDocument(**{
                "text": point.payload["text"],
                "score": point.score
            }
            ) for point in response.points
        ]
