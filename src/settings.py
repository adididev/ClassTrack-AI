import os
from urllib.parse import urlsplit

import streamlit as st


def get_setting(name, default=None):
    # Environment variables (Render, Docker) take priority, then .streamlit/secrets.toml
    value = os.environ.get(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return default


def get_app_url():
    # APP_URL can be set explicitly; otherwise use the address the host provides automatically
    url = get_setting("APP_URL") or os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        # Fall back to the domain the visitor is using (works on Streamlit Community Cloud)
        try:
            parts = urlsplit(st.context.url)
            if parts.scheme and parts.netloc:
                url = f"{parts.scheme}://{parts.netloc}"
        except Exception:
            pass
    return (url or "http://localhost:8501").rstrip("/")
