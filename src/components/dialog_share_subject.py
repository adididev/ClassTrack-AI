import streamlit as st

import segno
import io

from src.settings import get_app_url


@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):
    join_url = f"{get_app_url()}/?join-code={subject_code}"

    st.header("Scan to Join")

    qr = segno.make(join_url)

    out = io.BytesIO()

    qr.save(out, kind='png', scale=10, border=1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### Copy Link')
        st.code(join_url, language="text")
        st.code(subject_code, language="text")
        st.info('Share this link on WhatsApp or email, or give students the subject code.')

    with col2:
        st.markdown('### Scan to Join')
        st.image(out.getvalue(), caption='Scan with a phone camera to join')

        
