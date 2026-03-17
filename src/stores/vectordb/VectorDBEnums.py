from enum import Enum

class VectorDBEnum(Enum):

    QDRANT = "QDRANT"

class DistanceMethodsEnum(Enum):
    
    COSINE = "cosine"
    DOT = "dot"