import streamlit as st
from src.database.db import create_subject



@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of the new subject.")
    sub_id = st.text_input("Subject Code", placeholder="CS101")
    sub_name = st.text_input("Subject Name", placeholder="Introduction to Computer Science")
    sub_section = st.text_input("Section", placeholder="A")


    if st.button("Create Subject Now", type='primary', width='stretch'):
        if sub_id and sub_name and sub_section:
            clean_code = sub_id.strip()
            try:
                create_subject(clean_code, sub_name.strip(), sub_section.strip(), teacher_id)
                st.toast("Subject created")
                st.rerun()
            except Exception as e:
                err_str = str(e)
                if '23505' in err_str or 'unique constraint' in err_str or 'already exists' in err_str:
                    st.error(f"Subject Code '{clean_code}' already exists! Please enter a unique subject code.")
                else:
                    st.error("Couldn't create the subject. Please try again.")
        else:
            st.warning("Please fill in all the fields.")
