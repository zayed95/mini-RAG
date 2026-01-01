from .BaseController import BaseController
from fastapi import UploadFile
import os

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    # This function checks if the project directory exists, it creates it if it doesn't exist
    def get_project_directory(self, project_id: str):
        project_dir = os.path.join(
            self.file_dir,
            project_id
        )

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        
        return project_dir