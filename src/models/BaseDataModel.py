from helpers.config import get_settings, Settings

class BaseDataModel:
    def __init__(self, mongodb_client: object,settings: Settings = get_settings()):
        self.settings = settings
        self.db_client = mongodb_client