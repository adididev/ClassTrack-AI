import streamlit as st

from src.branding import PRIMARY, ACCENT, INK, SURFACE

def subject_card(name, code, section, stats=None, footer_callback=None):
    html = f"""
        <div style="background:white; border: 1px solid #CBD5E1; border-left: 8px solid {ACCENT}; padding:25px; border-radius: 20px; margin-bottom:20px; box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);">
        <h3 style="margin:0; color: {INK}; font-size: 1.5rem ">{name}</h3>
        <p style="color:#64748b; margin:10px 0;">Code : <span style="background:{SURFACE}; color:{PRIMARY}; font-weight:600; padding:2px 8px; border-radius:5px;">{code} </span> | Section : {section}</p>
        
        """
    
    if stats:
        html += """
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:12px;">
        """
        for icon, label, value in stats:
            html += f'<div style="background: #ECFDF5; color: #065F46; padding: 6px 14px; border-radius: 12px; font-size: 0.92rem; font-weight: 600; display: flex; align-items: center; gap: 4px;"><span>{icon}</span> <b style="color: #047857;">{value}</b> <span>{label}</span></div>'
        
        html += "</div>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
