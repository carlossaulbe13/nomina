import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS', 'serviceAccountKey.json')
    FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL', 'https://nomina-790b9-default-rtdb.firebaseio.com')
