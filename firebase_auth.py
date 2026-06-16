"""
Firebase Authentication & Firestore utilities for Exam Assistant AI.
Handles sign-up, login, logout, session restore, and user-specific chat persistence.
"""

import streamlit as st
import requests
import json
from datetime import datetime


# ---------------------------------------------------------------------------
# Helpers to read Firebase config from Streamlit secrets
# ---------------------------------------------------------------------------

def get_firebase_config():
    """Read Firebase project config from st.secrets."""
    try:
        return {
            "apiKey":            st.secrets["FIREBASE_API_KEY"],
            "projectId":         st.secrets["FIREBASE_PROJECT_ID"],
            "databaseURL":       st.secrets.get("FIREBASE_DATABASE_URL", ""),
        }
    except (KeyError, FileNotFoundError) as e:
        st.error(f"Firebase config missing in secrets: {e}")
        st.stop()


def get_firebase_api_key():
    return get_firebase_config()["apiKey"]


def get_project_id():
    return get_firebase_config()["projectId"]


# ---------------------------------------------------------------------------
# Firebase Auth REST helpers (no Admin SDK required)
# ---------------------------------------------------------------------------

AUTH_BASE = "https://identitytoolkit.googleapis.com/v1/accounts"


def _auth_post(endpoint: str, payload: dict) -> dict:
    """POST to Firebase Auth REST API and return JSON response."""
    api_key = get_firebase_api_key()
    url = f"{AUTH_BASE}:{endpoint}?key={api_key}"
    resp = requests.post(url, json=payload, timeout=10)
    return resp.json()


def sign_up(email: str, password: str, display_name: str) -> dict:
    """Create a new Firebase Auth user and store profile in Firestore."""
    data = _auth_post("signUp", {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    })
    if "idToken" in data:
        # Update display name
        _auth_post("update", {
            "idToken": data["idToken"],
            "displayName": display_name,
            "returnSecureToken": True,
        })
        # Persist user profile in Firestore
        _create_user_profile(data["localId"], email, display_name)
        return {"success": True, "user": data}
    error_msg = data.get("error", {}).get("message", "Sign-up failed.")
    return {"success": False, "error": _friendly_error(error_msg)}


def sign_in(email: str, password: str) -> dict:
    """Authenticate with email/password and return tokens."""
    data = _auth_post("signInWithPassword", {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    })
    if "idToken" in data:
        return {"success": True, "user": data}
    error_msg = data.get("error", {}).get("message", "Login failed.")
    return {"success": False, "error": _friendly_error(error_msg)}


def refresh_token(refresh_tok: str) -> dict:
    """Exchange a refresh token for a new ID token."""
    api_key = get_firebase_api_key()
    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    resp = requests.post(url, json={
        "grant_type": "refresh_token",
        "refresh_token": refresh_tok,
    }, timeout=10)
    data = resp.json()
    if "id_token" in data:
        return {"success": True, "idToken": data["id_token"], "refreshToken": data["refresh_token"]}
    return {"success": False, "error": "Session expired. Please log in again."}


def get_user_info(id_token: str) -> dict:
    """Fetch user profile from Firebase Auth using a valid ID token."""
    data = _auth_post("lookup", {"idToken": id_token})
    if "users" in data:
        return {"success": True, "user": data["users"][0]}
    return {"success": False, "error": "Could not fetch user info."}


def _friendly_error(code: str) -> str:
    mapping = {
        "EMAIL_EXISTS":              "This email is already registered. Please log in.",
        "INVALID_EMAIL":             "Invalid email address.",
        "WEAK_PASSWORD":             "Password must be at least 6 characters.",
        "EMAIL_NOT_FOUND":           "No account found with this email.",
        "INVALID_PASSWORD":          "Incorrect password.",
        "USER_DISABLED":             "This account has been disabled.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many failed attempts. Try again later.",
        "INVALID_LOGIN_CREDENTIALS": "Incorrect email or password.",
    }
    for key, msg in mapping.items():
        if key in code:
            return msg
    return code


# ---------------------------------------------------------------------------
# Firestore REST helpers
# ---------------------------------------------------------------------------

def _fs_url(path: str) -> str:
    project_id = get_project_id()
    return f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/{path}"


def _fs_headers(id_token: str) -> dict:
    return {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}


def _to_fs_value(v):
    """Convert a Python value to a Firestore REST value dict."""
    if isinstance(v, bool):
        return {"booleanValue": v}
    if isinstance(v, int):
        return {"integerValue": str(v)}
    if isinstance(v, float):
        return {"doubleValue": v}
    if isinstance(v, str):
        return {"stringValue": v}
    if isinstance(v, datetime):
        return {"timestampValue": v.isoformat() + "Z"}
    return {"stringValue": str(v)}


def _from_fs_value(v: dict):
    """Convert a Firestore REST value dict to a Python value."""
    if "stringValue" in v:
        return v["stringValue"]
    if "integerValue" in v:
        return int(v["integerValue"])
    if "doubleValue" in v:
        return v["doubleValue"]
    if "booleanValue" in v:
        return v["booleanValue"]
    if "timestampValue" in v:
        return v["timestampValue"]
    if "nullValue" in v:
        return None
    return str(v)


def _doc_to_dict(doc: dict) -> dict:
    fields = doc.get("fields", {})
    return {k: _from_fs_value(vv) for k, vv in fields.items()}


# ---------------------------------------------------------------------------
# User profile
# ---------------------------------------------------------------------------

def _create_user_profile(uid: str, email: str, display_name: str):
    """Write user profile to Firestore (no auth token needed at sign-up time via service-level write)."""
    # We store this right after sign-up; use the ID token obtained in sign_up caller
    # Actually, we just queue it — profile is written by the authenticated flow after login.
    # Store temporarily in a module-level dict to be committed post-login.
    _pending_profiles[uid] = {
        "email": email,
        "displayName": display_name,
        "createdAt": datetime.utcnow().isoformat() + "Z",
    }


_pending_profiles: dict = {}


def flush_user_profile(uid: str, id_token: str):
    """Write pending user profile to Firestore after we have a valid token."""
    if uid not in _pending_profiles:
        return
    profile = _pending_profiles.pop(uid)
    fields = {k: _to_fs_value(v) for k, v in profile.items()}
    url = _fs_url(f"users/{uid}")
    requests.patch(url, headers=_fs_headers(id_token),
                   json={"fields": fields}, timeout=10)


def get_user_profile(uid: str, id_token: str) -> dict:
    """Fetch user profile from Firestore."""
    url = _fs_url(f"users/{uid}")
    resp = requests.get(url, headers=_fs_headers(id_token), timeout=10)
    if resp.status_code == 200:
        return _doc_to_dict(resp.json())
    return {}


# ---------------------------------------------------------------------------
# Chat session management
# ---------------------------------------------------------------------------

def create_chat_session(uid: str, id_token: str) -> str | None:
    """Create a new chat session document and return its session ID."""
    import uuid
    session_id = str(uuid.uuid4())
    url = _fs_url(f"chat_sessions/{session_id}")
    fields = {
        "userId":    _to_fs_value(uid),
        "createdAt": _to_fs_value(datetime.utcnow().isoformat() + "Z"),
    }
    resp = requests.patch(url, headers=_fs_headers(id_token),
                          json={"fields": fields}, timeout=10)
    if resp.status_code == 200:
        return session_id
    return None


def get_user_sessions(uid: str, id_token: str) -> list[dict]:
    """Fetch all chat sessions for a user, newest first."""
    project_id = get_project_id()
    url = (
        f"https://firestore.googleapis.com/v1/projects/{project_id}"
        f"/databases/(default)/documents:runQuery"
    )
    body = {
        "structuredQuery": {
            "from": [{"collectionId": "chat_sessions"}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": "userId"},
                    "op": "EQUAL",
                    "value": {"stringValue": uid},
                }
            },
            "orderBy": [{"field": {"fieldPath": "createdAt"}, "direction": "DESCENDING"}],
            "limit": 20,
        }
    }
    resp = requests.post(url, headers=_fs_headers(id_token), json=body, timeout=10)
    sessions = []
    if resp.status_code == 200:
        for item in resp.json():
            doc = item.get("document")
            if doc:
                name = doc["name"].split("/")[-1]
                d = _doc_to_dict(doc)
                d["sessionId"] = name
                sessions.append(d)
    return sessions


def save_message(session_id: str, role: str, content: str, id_token: str):
    """Append a message to a chat session in Firestore."""
    import uuid
    msg_id = str(uuid.uuid4())
    url = _fs_url(f"messages/{msg_id}")
    fields = {
        "sessionId": _to_fs_value(session_id),
        "role":      _to_fs_value(role),
        "content":   _to_fs_value(content),
        "timestamp": _to_fs_value(datetime.utcnow().isoformat() + "Z"),
    }
    requests.patch(url, headers=_fs_headers(id_token),
                   json={"fields": fields}, timeout=10)


def load_messages(session_id: str, id_token: str) -> list[dict]:
    """Load all messages for a session, ordered by timestamp."""
    project_id = get_project_id()
    url = (
        f"https://firestore.googleapis.com/v1/projects/{project_id}"
        f"/databases/(default)/documents:runQuery"
    )
    body = {
        "structuredQuery": {
            "from": [{"collectionId": "messages"}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": "sessionId"},
                    "op": "EQUAL",
                    "value": {"stringValue": session_id},
                }
            },
            "orderBy": [{"field": {"fieldPath": "timestamp"}, "direction": "ASCENDING"}],
        }
    }
    resp = requests.post(url, headers=_fs_headers(id_token), json=body, timeout=10)
    messages = []
    if resp.status_code == 200:
        for item in resp.json():
            doc = item.get("document")
            if doc:
                messages.append(_doc_to_dict(doc))
    return messages


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------

def init_auth_state():
    """Initialise auth-related keys in st.session_state."""
    defaults = {
        "authenticated": False,
        "user_id":        None,
        "user_email":     None,
        "user_name":      None,
        "id_token":       None,
        "refresh_token":  None,
        "session_id":     None,
        "auth_page":      "login",   # "login" | "signup"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def restore_session() -> bool:
    """
    Try to restore session from a persisted refresh token.
    Returns True if session was successfully restored.
    """
    rt = st.session_state.get("refresh_token")
    if not rt:
        return False
    result = refresh_token(rt)
    if result["success"]:
        st.session_state.id_token      = result["idToken"]
        st.session_state.refresh_token = result["refreshToken"]
        # Refresh user info
        info = get_user_info(result["idToken"])
        if info["success"]:
            u = info["user"]
            st.session_state.authenticated = True
            st.session_state.user_id       = u["localId"]
            st.session_state.user_email    = u.get("email", "")
            st.session_state.user_name     = u.get("displayName") or u.get("email", "User")
        return st.session_state.authenticated
    # Token expired — clear
    logout()
    return False


def logout():
    """Clear all session data."""
    keys_to_clear = [
        "authenticated", "user_id", "user_email", "user_name",
        "id_token", "refresh_token", "session_id",
        "messages", "question_count", "prefill", "uploads",
        "greeted", "indexed_files", "vectorstore",
    ]
    for k in keys_to_clear:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state.auth_page = "login"
