"""Fonctions utilitaires pour les appels à l'API backend."""

import streamlit as st
import requests
import json
from typing import Optional, Dict, Any, Generator

from config import API_BASE_URL

# ---------- Gestion des erreurs ----------
def _handle_connection_error():
    st.error("Connection failed: The backend is not reachable. Please ensure it is running on " + API_BASE_URL)

def _handle_http_error(response: requests.Response):
    try:
        detail = response.json().get("detail", response.text)
    except Exception:
        detail = response.text
    if response.status_code == 401:
        st.error("Session expired. Please sign in again.")
        if "token" in st.session_state:
            del st.session_state["token"]
            st.rerun()
    elif response.status_code == 429:
        st.error("Rate limit exceeded. Please wait a moment and try again.")
    else:
        st.error(f"Request error ({response.status_code}): {detail}")

# ---------- Fonctions génériques ----------
def api_get(
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 120  # <-- augmenté pour Render cold start
) -> Optional[Any]:
    """Send a GET request and return parsed JSON, or None on failure."""
    try:
        resp = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        _handle_connection_error()
    except requests.exceptions.HTTPError:
        _handle_http_error(resp)
    except Exception as e:
        st.error(f"Network error: {e}")
    return None

def api_post(
    endpoint: str,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 120  # <-- augmenté
) -> Optional[Any]:
    """Send a POST request and return parsed JSON, or None on failure."""
    try:
        resp = requests.post(f"{API_BASE_URL}{endpoint}", json=json, data=data, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        _handle_connection_error()
    except requests.exceptions.HTTPError:
        _handle_http_error(resp)
    except Exception as e:
        st.error(f"Network error: {e}")
    return None

def api_put(
    endpoint: str,
    json: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 120  # <-- augmenté
) -> Optional[Any]:
    """Send a PUT request and return parsed JSON, or None on failure."""
    try:
        resp = requests.put(f"{API_BASE_URL}{endpoint}", json=json, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        _handle_connection_error()
    except requests.exceptions.HTTPError:
        _handle_http_error(resp)
    except Exception as e:
        st.error(f"Network error: {e}")
    return None

def api_delete(
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 120  # <-- augmenté
) -> bool:
    """Send a DELETE request. Returns True on success, False otherwise."""
    try:
        resp = requests.delete(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=timeout)
        resp.raise_for_status()
        return True
    except requests.exceptions.ConnectionError:
        _handle_connection_error()
    except requests.exceptions.HTTPError:
        _handle_http_error(resp)
    except Exception as e:
        st.error(f"Network error: {e}")
    return False

def api_post_stream(
    endpoint: str,
    json_data: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 180  # <-- très long pour le streaming après cold start
) -> Generator[str, None, None]:
    """Send a POST request for streaming and yield tokens (SSE format)."""
    try:
        with requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=json_data,
            headers=headers,
            stream=True,
            timeout=timeout
        ) as resp:
            resp.raise_for_status()
            st.caption(f"Stream status: {resp.status_code}")
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])   # le module json est bien accessible
                        if "token" in data:
                            yield data["token"]
                        elif "error" in data:
                            st.error(f"Stream error from backend: {data['error']}")
                            break
                    except json.JSONDecodeError:
                        continue
    except requests.exceptions.ConnectionError:
        _handle_connection_error()
    except requests.exceptions.HTTPError:
        _handle_http_error(resp)
    except Exception as e:
        st.error(f"Streaming error: {e}")
