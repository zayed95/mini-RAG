from enum import Enum

class ResponseSignal(Enum):

    FILE_UPLOAD_FAILED = 'file_upload_failed'
    FILE_SIZE_EXCEEDED = 'file_size_exeeded'
    FILE_TYPE_NOT_SUPPORTED = 'file_type_not_supported'
    FILE_UPLOAD_SUCCESS = 'file_uploaded_successfully'