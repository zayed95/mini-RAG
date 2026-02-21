from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import re, os

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576

    # A function to check the validity of the uploaded file    
    def validate_file(self, file: UploadFile):

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > (self.app_settings.FILE_MAX_SIZE * self.size_scale):
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True, ResponseSignal.FILE_UPLOAD_SUCCESS.value
    
    # A function used to generate unique name for each file
    def generate_unique_file_path(self, original_filename: str, project_id: str):

        # Get random string
        random_string = self.generate_random_string()

        # Get the project path
        project_path = ProjectController().get_project_directory(project_id)

        # Remove unecessary characters from the original filename
        clean_filename = self.get_clean_filename(original_filename)

        # Combine the clean filename with the random string
        new_file_path = os.path.join(
            project_path,
            random_string + "_" + clean_filename
        )

        while os.path.exists(new_file_path):
            random_string = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_string + "_" + new_file_path
            )

        return new_file_path, random_string + "_" + new_file_path

    def get_clean_filename(self, original_filename: str):

        cleaned_file_name = re.sub(r'[^\w.]', '', original_filename.strip())
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name
    