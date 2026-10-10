import streamlit as st

from src.branding import APP_NAME, APP_TAGLINE, PRIVACY_URL, LANDING_URL


def _footer(color, link_color):
    st.markdown(f"""
        <p style='text-align:center; color:{color}; font-size:0.85rem; margin-top:40px;'>
            {APP_NAME} &middot; {APP_TAGLINE}<br>
            <a href='{LANDING_URL}/about' target='_blank' style='color:{link_color};'>About</a> &middot;
            <a href='{PRIVACY_URL}' target='_blank' style='color:{link_color};'>Privacy Policy</a>
        </p>
    """, unsafe_allow_html=True)


def footer_home():
    _footer('#DBEAFE', '#FFFFFF')


def footer_dashboard():
    _footer('#64748B', '#2563EB')
