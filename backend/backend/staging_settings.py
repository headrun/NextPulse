from backend.settings import *
from db_config import *

DATABASES['default'].update(db_config. DEFAULT_STAGING_DATABASE_CONFIG)
