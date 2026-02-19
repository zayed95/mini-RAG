from helpers.config import get_settings, Settings
import os, random, string

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

    # Random strings generation function
    def generate_random_string(self, length: str=12):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))