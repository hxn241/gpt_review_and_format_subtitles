import os
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.realpath('__file__'))

load_dotenv()


class Config:

    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = "gpt-3.5-turbo-16k"
    OPENAI_MAX_TOKENS = 500
    OPENAI_TEMPERATURE = 0
    REPTRAK_MODEL = 'babbage:ft-personal-2023-02-13-20-47-23'
    # REPTRAK_MODEL = 'babbage:ft-personal-2023-02-12-19-58-21'

    CORE_BASE_URL = 'http://core-rest-api.acceso.int:90/item'
    CORE_USER = 'test'
    CORE_DEFAULT_REQUEST_PAGE_SIZE = 500
    CORE_MAX_ITERATIONS = 40
    CORE_MAX_TIMEOUT = 9000
