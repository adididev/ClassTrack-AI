import base64
import streamlit as st

from src.branding import APP_TAGLINE, LOGO_PATH, PRIMARY, ACCENT, INK


@st.cache_data
def get_logo_data_url():
    try:
        with open(LOGO_PATH, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    except Exception:
        return ""


def header_home():
    logo_data_url = get_logo_data_url()
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px; margin-top:30px">
            <img src='{logo_data_url}' style='height:110px; object-fit:contain;' />
            <h1 style='text-align:center; color:#FFFFFF; margin-top:12px;'>ClassTrack <span style='color:{ACCENT};'>AI</span></h1>
            <p style='text-align:center; color:#DBEAFE; font-size:1.1rem; margin-top:8px;'>{APP_TAGLINE}</p>
        </div>   
    """, unsafe_allow_html=True)


def header_dashboard():
    logo_data_url = get_logo_data_url()
    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:center; gap:15px">
            <img src='{logo_data_url}' style='height:80px; object-fit:contain;' />
            <h2 style='text-align:left; color:{INK} !important; margin:0;'>ClassTrack <span style='color:{PRIMARY};'>AI</span></h2>
        </div>   
    """, unsafe_allow_html=True)
