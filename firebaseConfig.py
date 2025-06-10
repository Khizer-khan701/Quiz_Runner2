import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ✅ Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

# ✅ Create and export Firestore client
db = firestore.client()
