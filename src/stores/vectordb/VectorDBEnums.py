from enum  import Enum

class VectorDBEnums(Enum):
    
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"


class DistanceMetricEnums(Enum):
    
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT = "dot"


class PgVectorTableSchemeEnums(Enum):
    
    ID = "id"
    VECTOR = "vector"
    TEXT = "text"
    CHUNK_ID = "chunk_id"
    METADATA = "metadata"
    _PREFIX = "pgvector"

class PgVectorDistanceMethodEnums(Enum):
    
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"

class PgVectorIndexTypeEnums(Enum):
    
    IVFFLAT = "ivfflat"
    HNSW = "hnsw"