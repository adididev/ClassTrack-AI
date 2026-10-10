import streamlit as st

from src.branding import PRIMARY, PRIMARY_DARK, ACCENT, INK, SURFACE, SURFACE_CARD



def style_background_home():

    st.markdown(f"""
        <style>

                .stApp {{
                    background: linear-gradient(160deg, {PRIMARY_DARK} 0%, {PRIMARY} 55%, #3B82F6 100%) !important;
                }}

                .stApp div[data-testid="stColumn"]{{
                    background-color:{SURFACE_CARD} !important;
                    padding:2.5rem !important;
                    border-radius: 2rem !important;
                    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.25) !important;
                    border-top: 6px solid {ACCENT} !important;
                    }}
        </style>  

                """
            ,unsafe_allow_html=True)
    

def style_background_dashboard():

    st.markdown(f"""
        <style>

                .stApp {{
                    background: {SURFACE} !important;
                }}

        </style>  

                """
            ,unsafe_allow_html=True)
    

    

def style_base_layout():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

                
         /* Hide Top Bar of streamlit */
                
            #MainMenu, footer, header {{
                visibility: hidden;
            }}
                
            .block-container {{
                padding-top:1.5rem !important;    
            }}

            h1 {{
                font-family: 'Sora', sans-serif !important;
                font-size: 2.75rem !important;
                font-weight: 800 !important;
                letter-spacing: -0.03em !important;
                line-height: 1.1 !important;
                margin-bottom: 0rem !important;
            }}
                

            h2 {{
                font-family: 'Sora', sans-serif !important;
                font-size: 1.75rem !important;
                font-weight: 700 !important;
                letter-spacing: -0.02em !important;
                line-height: 1.2 !important;
                margin-bottom: 0rem !important;
                color: {INK} !important;
            }}
                
            h3, h4, p, label, button, input {{
                font-family: 'Inter', sans-serif !important;    
            }}
                

            button{{
                border-radius: 0.85rem !important;
                background-color: {PRIMARY} !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                font-weight: 600 !important;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out !important;
                }}

            button[kind="secondary"]{{
                border-radius: 0.85rem !important;
                background-color: {ACCENT} !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out !important;
                }}

            button[kind="tertiary"]{{
                border-radius: 0.85rem !important;
                background-color: {INK} !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out !important;
                }}

            button:hover{{
                transform :translateY(-2px);
                box-shadow: 0 8px 18px rgba(37, 99, 235, 0.3) !important;
                }}

            /* Make disabled buttons look disabled (e.g. Create Account before consent) */
            button:disabled, button:disabled:hover{{
                opacity: 0.45 !important;
                cursor: not-allowed !important;
                transform: none !important;
                box-shadow: none !important;
                }}
        </style>  

                """
            ,unsafe_allow_html=True)
