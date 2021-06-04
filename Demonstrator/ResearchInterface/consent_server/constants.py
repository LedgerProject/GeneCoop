"""
    Shared constants for db config and urls
"""
from django.conf import settings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# DataBase fields
TITLE_LENGTH = 200
DESCR_LENGTH = 1000
TOKEN_LENGTH = 50
USERID_LENGTH = 50
EXPERIMENTS_LENGTH = 1000
# USERID_LENGTH = 200
TYPE_LENGTH = 30
LOGMESSAGE_LENGTH = 500
SIGNATURE_LENGTH = 500
SIGNEDVC_LENGTH = 20000
PUBLICKEY_LENGTH = 500
QUESTION_LENGTH = 100
ANSWER_LENGTH = 100

# Urls
if settings.DEBUG == True:
    GENECOOP_URL = 'http://localhost:8000'
else:
    GENECOOP_URL = 'https://genecoop.waag.org'

ISSIGNED_URL = f"{GENECOOP_URL}/consent/api/is_signed"
ALLOWEDEXP_URL = f"{GENECOOP_URL}/consent/api/allowed_experiments"
LOGEXP_URL = f"{GENECOOP_URL}/consent/api/log_experiment/"

APIROOM_URL = 'http://localhost:3000'

SIGN_URL = f'{APIROOM_URL}/api/zencoop/sign'
VERIFY_URL = f'{APIROOM_URL}/api/zencoop/verify'

# Config param
DO_ENCODING = False

GC_SCHEMA = 'http://genecoop.waag.org/schema/v1#'
GC_CRED = 'http://genecoop.waag.org/credentials/v1#'

