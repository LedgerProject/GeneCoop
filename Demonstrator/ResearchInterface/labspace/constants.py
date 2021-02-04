"""
    Shared constants for db config
"""

TITLE_LENGTH = 200
DESCR_LENGTH = 1000
TOKEN_LENGTH = 2000
OPERATIONS_LENGTH = 1000
USERID_LENGTH = 200
TYPE_LENGTH = 30
LOGMESSAGE_LENGTH = 500
KEY_LENGTH = 500
SIGNATURE_LENGTH = 10000

GENECOOP_URL = 'http://localhost:8000'
ISSIGNED_URL = f"{GENECOOP_URL}/consent/api/is_signed"
ALLOWEDOP_URL = f"{GENECOOP_URL}/consent/api/allowed_operations"
LOGOP_URL = f"{GENECOOP_URL}/consent/api/log_operation/"

APIROOM_URL = 'http://localhost:3000'

