import json
import os
import firebase_admin
from firebase_admin import credentials

_initialized = False


def init_firebase(cred_path, database_url):
    global _initialized
    if _initialized:
        return
    cred_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
    else:
        cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {'databaseURL': database_url})
    _initialized = True
