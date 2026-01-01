from helpers.config import get_settings, Settings
import os

class BaseController:

    def __init__(self):

        # Retreving the project configuration
        self.app_settings = get_settings()

        # Getting the path of the base directory
        self.base_dir = os.path.dirname(os.path.dirname(__file__))

        # Defining the pathe of the file using os library to 
        self.file_dir = os.path.join(
            self.base_dir,
            "assets/files"
        )