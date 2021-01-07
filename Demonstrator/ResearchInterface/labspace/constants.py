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

HOST = 'http://localhost:8000'
ISSIGNED_URL = f"{HOST}/api/is_signed"
ALLOWEDOP_URL = f"{HOST}/api/allowed_operations"
