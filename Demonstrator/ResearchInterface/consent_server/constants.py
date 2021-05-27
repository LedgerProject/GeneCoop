"""
    Shared constants for db config
"""

# DataBase fields
TITLE_LENGTH = 200
DESCR_LENGTH = 1000
TOKEN_LENGTH = 50
EXPERIMENTS_LENGTH = 1000
# USERID_LENGTH = 200
TYPE_LENGTH = 30
LOGMESSAGE_LENGTH = 500
SIGNATURE_LENGTH = 500
SIGNEDVC_LENGTH = 20000
PUBLICKEY_LENGTH = 500

# Urls
GENECOOP_URL = 'http://localhost:8000'
ISSIGNED_URL = f"{GENECOOP_URL}/consent/api/is_signed"
ALLOWEDEXP_URL = f"{GENECOOP_URL}/consent/api/allowed_experiments"
LOGEXP_URL = f"{GENECOOP_URL}/consent/api/log_experiment/"

APIROOM_URL = 'http://localhost:3000'

SIGN_URL = f'{APIROOM_URL}/api/zencoop/sign'
VERIFY_URL = f'{APIROOM_URL}/api/zencoop/verify'

# Config param
DO_ENCODING = False