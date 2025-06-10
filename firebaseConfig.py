import firebase_admin # type: ignore
from firebase_admin import credentials, firestore # type: ignore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
