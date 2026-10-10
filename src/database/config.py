import streamlit as st


from supabase import create_client, Client

from src.settings import get_setting

SUPABASE_URL = get_setting("SUPABASE_URL")
SUPABASE_KEY = get_setting("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("ClassTrack AI is not configured: set SUPABASE_URL and SUPABASE_KEY as environment variables or in .streamlit/secrets.toml")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
