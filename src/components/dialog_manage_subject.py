import streamlit as st

from src.database.db import update_subject, delete_subject


@st.dialog("Edit Subject")
def edit_subject_dialog(subject):
    st.write(f"Subject code **{subject['subject_code']}** stays the same, so existing join links keep working.")
    new_name = st.text_input("Subject Name", value=subject['name'])
    new_section = st.text_input("Section", value=subject['section'] or "")

    if st.button("Save changes", type='primary', width='stretch'):
        if new_name.strip() and new_section.strip():
            try:
                update_subject(subject['subject_id'], new_name.strip(), new_section.strip())
                st.toast("Subject updated")
                st.rerun()
            except Exception:
                st.error("Couldn't update the subject. Please try again.")
        else:
            st.warning("Please fill in all the fields.")


@st.dialog("Delete Subject")
def delete_subject_dialog(subject):
    st.warning(
        f"This permanently deletes **{subject['name']} ({subject['subject_code']})**, "
        "removes all enrolled students from it, and deletes its attendance records. This can't be undone."
    )
    confirm_code = st.text_input(f"Type {subject['subject_code']} to confirm")

    if st.button("Delete subject", type='primary', width='stretch', disabled=confirm_code.strip() != subject['subject_code']):
        try:
            delete_subject(subject['subject_id'])
            st.toast("Subject deleted")
            st.rerun()
        except Exception:
            st.error("Couldn't delete the subject. Please try again.")
