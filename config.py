import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_TYPE = 'filesystem'

    # Azure Storage
    AZURE_STORAGE_CONNECTION_STRING = \
        os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')

    # Azure AI Search
    AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
    AZURE_SEARCH_API_KEY = os.getenv('AZURE_SEARCH_API_KEY')
    AZURE_SEARCH_INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME',
                                        'cloudfolio-index')

    # User storage
    USERS_FILE = 'users.json'

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
