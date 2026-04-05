from enum import Enum

class ResponseSignal(Enum):

    FILE_UPLOAD_FAILED = 'file_upload_failed'
    FILE_SIZE_EXCEEDED = 'file_size_exeeded'
    FILE_TYPE_NOT_SUPPORTED = 'file_type_not_supported'
    FILE_UPLOAD_SUCCESS = 'file_uploaded_successfully'
    PROCESSING_FAIL = 'processing_failed'
    PROCESSING_SUCCESS = 'processing_succeeded'
    NO_FILES_ERROR = 'no_files_found'
    FILE_ID_ERROR='no_file_found_with_that_id'
    PROJECT_NOT_FOUND_ERROR = "project_not_found"
    INSERT_INTO_VECTOR_DB_ERROR = "could_not_insert_into_vectordb"
    INSERT_INTO_VECTOR_DB_SUCCESS = "insert_into_vectordb_success"
    VECTORDB_COLLECTION_RETRIEVED = "vectordb_collection_retrieved"
    VECTORDB_SEARCH_ERROR = "vectordb_search_error"
    VECTORDB_SEARCH_SUCCESS = "vectordb_search_success"
