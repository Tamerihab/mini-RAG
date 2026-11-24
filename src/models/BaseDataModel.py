from helpers.config import get_settings, Settings

class BaseDataModel:
    def __init__(self, db_client: object, settings: Settings = get_settings()):
        self.settings = settings
        self.db_client = db_client