import os


EVENT_DB_HOST = os.getenv('EVENT_DB_HOST')
EVENT_DB_USER = os.getenv('EVENT_DB_USER')
EVENT_DB_PASS = os.getenv('EVENT_DB_PASS')
EVENT_DB_TYPE = os.getenv('EVENT_DB_TYPE', 'postgresql')
EVENT_DB_POOL_SIZE = os.getenv('EVENT_DB_POOL_SIZE', 5)
