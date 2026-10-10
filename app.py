import logging

import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen

from src.components.dialog_auto_enroll import auto_enroll_dialog
from src.branding import APP_NAME, LOGO_PATH, GITHUB_URL

logger = logging.getLogger(__name__)

def main():
    st.set_page_config(
        page_title=f'{APP_NAME} - Making Attendance faster using AI',
        page_icon= LOGO_PATH
    )
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()

        case 'student':
            student_screen()
        
        case None:
            home_screen()


    join_code = st.query_params.get('join-code')
    if join_code:
        if st.session_state.login_type != 'student':
            st.session_state.login_type = 'student'
            st.rerun()
        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
            auto_enroll_dialog(join_code)


try:
    main()
except Exception:
    # st.rerun()/st.stop() use BaseException, so only real errors land here.
    # Show a friendly message; the full traceback goes to the server logs.
    logger.exception("Unhandled error")
    st.error(
        "Something went wrong on our side. Please refresh the page and try again. "
        f"If it keeps happening, [report it on GitHub]({GITHUB_URL}/issues)."
    )