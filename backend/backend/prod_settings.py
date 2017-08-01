from backend.settings import *
import db_config

DATABASES['default'].update(db_config. DEFAULT_PROD_DATABASE_CONFIG)
