import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS', 'serviceAccountKey.json')
    FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL', 'https://nomina-790b9-default-rtdb.firebaseio.com')


if not Config.SECRET_KEY:
    raise RuntimeError(
        'Falta SECRET_KEY. Sin ella Flask firmaba las cookies de sesion con un valor '
        'por defecto que esta en el repo publico, y cualquiera podia forjarse una '
        'sesion con role=admin. Definela en .env (local) o en las variables de '
        'Railway (produccion).'
    )
