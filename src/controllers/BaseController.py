from helpers.config import get_settings, Settings
import os, random, string

class BaseController:

    def __init__(self):

        # Retreving the project configuration
        self.app_settings = get_settings()

        # Get the path of the base directory
        self.base_dir = os.path.dirname(os.path.dirname(__file__))

        self.file_dir = os.path.join(
            self.base_dir,
            "assets/files"
        )

        # Set the path to the vectorDB
        self.database_dir = os.path.join(
            self.base_dir,
            "assets/database"
        )

    # Random strings generation function
    def generate_random_string(self, length: str=12):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def get_database_path(self, db_name: str):
        
        database_path = os.path.join(self.database_dir, db_name)

        if not os.path.exists(database_path):
            os.makedirs(database_path)

        return database_path