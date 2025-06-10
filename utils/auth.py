import requests
from firebaseConfig import db

FIREBASE_API_KEY = "AIzaSyBhHCnlhEs_zlBgvbBoQiE30bSexqYGlF4"

def signup_user(email, password, name, role):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        uid = data['localId']
        db.collection('users').document(uid).set({
            'email': email,
            'name': name,
            'role': role
        })
        return True, "Account created successfully!", uid
    else:
        error = response.json().get('error', {}).get('message', 'Unknown error')
        return False, error, None

def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        uid = data["localId"]
        return True, "Login successful", uid
    else:
        error = response.json().get("error", {}).get("message", "Unknown error")
        return False, error, None

def get_user_info(uid):
    doc = db.collection('users').document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None

def send_password_reset(email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return True, "Password reset email sent."
    else:
        error = response.json().get("error", {}).get("message", "Unknown error")
        return False, error
