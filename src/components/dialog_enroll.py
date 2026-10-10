import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase

import time


@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.write('Enter the subject code your teacher shared with you.')
    join_code = st.text_input('Subject Code', placeholder='Eg. CS101')

    if st.button('Enroll now', type='primary', width='stretch'):
        join_code = join_code.strip()
        if join_code:
            res = supabase.table('subjects').select('subject_id, name, subject_code').eq('subject_code', join_code).execute()
            if res.data:
                subject = res.data[0]
                student_id = st.session_state.student_data['student_id']

                check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
                if check.data:
                    st.info("You're already enrolled in this subject.")
                else:
                    enroll_student_to_subject(student_id, subject['subject_id'])
                    st.success(f"Enrolled in {subject['name']}.")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error(f"No subject found with code '{join_code}'. Check the code with your teacher (it is case-sensitive).")
        else:
            st.warning('Please enter a subject code.')