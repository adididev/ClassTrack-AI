import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subjects, get_attendance_for_teacher, set_attendance_status
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_manage_subject import edit_subject_dialog, delete_subject_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd

from src.database.config import supabase


from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.branding import PRIVACY_URL
import time

MIN_PASSWORD_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 60
def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()





def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {teacher_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data 
            st.rerun()


    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'
    tab1, tab2, tab3 = st.columns(3)


    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance',type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Attendance Records',type=type3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()


    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    


    footer_dashboard()

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')


    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.info("You haven't created any subjects yet. Go to Manage Subjects to create one.")
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4 ]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()


    with c2:
        
        if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Scanning classroom photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)


                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id',selected_subject_id ).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students are enrolled in this subject yet.')
                else:

                    results, attendance_to_log  = [], []

                    # Stored in UTC; Attendance Records converts to the teacher's timezone
                    current_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present= len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                    # Recognized faces that can't be marked because they aren't enrolled in this subject
                    enrolled_ids = {int(node['students']['student_id']) for node in enrolled_students}
                    not_enrolled_ids = [sid for sid in all_detected_ids if sid not in enrolled_ids]
                    note = None
                    if not_enrolled_ids:
                        res = supabase.table('students').select('student_id, name').in_('student_id', not_enrolled_ids).execute()
                        names = ", ".join(s['name'] for s in res.data) or f"{len(not_enrolled_ids)} student(s)"
                        note = f"Recognized but not enrolled in this subject: {names}. Ask them to enroll with the subject code so they can be marked present."

                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log, note)

    with c3:
        if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)











def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects', width='stretch')

    with col2:
        if st.button('Create New Subject', width='stretch'):
            create_subject_dialog(teacher_id)


    # LIST all SUBJECTS
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        cols = st.columns(2)
        for i, sub in enumerate(subjects):
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]
            def make_share_callback(s):
                def share_btn():
                    if st.button("Share join link", key=f"share_{s['subject_code']}_{s['subject_id']}", icon=":material/share:", width='stretch'):
                        share_subject_dialog(s['name'], s['subject_code'])
                    b2, b3 = st.columns(2)
                    with b2:
                        if st.button("Edit", key=f"edit_{s['subject_id']}", type='tertiary', icon=":material/edit:", width='stretch'):
                            edit_subject_dialog(s)
                    with b3:
                        if st.button("Delete", key=f"delete_{s['subject_id']}", type='tertiary', icon=":material/delete:", width='stretch'):
                            delete_subject_dialog(s)
                    st.space()
                return share_btn

            with cols[i % 2]:
                subject_card(
                    name = sub['name'],
                    code = sub['subject_code'],
                    section = sub['section'],
                    stats = stats,
                    footer_callback = make_share_callback(sub)
                )
    else:
        st.info("No subjects yet. Click Create New Subject to add one.")


def format_local_time(ts):
    # Timestamps are stored in UTC; show them in the teacher's browser timezone
    dt = datetime.fromisoformat(ts)
    try:
        if st.context.timezone:
            dt = dt.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(st.context.timezone))
    except Exception:
        pass
    return dt.strftime("%Y-%m-%d %I:%M %p")


def teacher_tab_attendance_records():
    st.header('Attendance Records')

    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info('No attendance saved yet. Take attendance and click "Confirm & Save" to see it here.')
        return
    
    data = []

    for r in records:
        ts = r.get('timestamp')

        data.append({
            "log_id": r.get('id'),
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": format_local_time(ts) if ts else "N'A",
            "Subject": r['subjects']['name'],
            "Subject Code":r['subjects']['subject_code'],
            "Student": (r.get('students') or {}).get('name', 'Unknown'),
            "is_present": bool(r.get('is_present', False))
        })


    df = pd.DataFrame(data)



    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count = ('is_present', 'sum'),
            Total_Count =('is_present', 'count')
        ).reset_index()

    )

    summary['Attendance Stats'] = (
        "✅ " + summary['Present_Count'].astype(str) + " /"
        + summary['Total_Count'].astype(str) + ' Students'
    )

    summary = summary.sort_values(by='ts_group' ,ascending=False)
    display_df = summary[['Time', 'Subject', 'Subject Code', 'Attendance Stats']]
    
    st.dataframe(display_df, width='stretch', hide_index=True)

    st.download_button(
        'Download all records (CSV)', data=attendance_csv(df), file_name='classtrack_attendance.csv',
        mime='text/csv', icon=':material/download:', type='tertiary',
    )

    # Per-student view of one session, editable so the teacher can correct mistakes
    st.subheader('Who was present?')
    sessions = {
        f"{row['Time']} · {row['Subject']} ({row['Subject Code']})": (row['ts_group'], row['Subject Code'])
        for _, row in summary.iterrows()
    }
    selected = st.selectbox('Select a class session', options=list(sessions.keys()))
    ts_group, subject_code = sessions[selected]

    session_df = (
        df[(df['ts_group'] == ts_group) & (df['Subject Code'] == subject_code)]
        .sort_values(by=['is_present', 'Student'], ascending=[False, True])
        .reset_index(drop=True)
    )
    present_count = int(session_df['is_present'].sum())
    st.caption(f"{present_count} of {len(session_df)} students present. Tick or untick **Present** to correct a mistake, then save.")

    edited = st.data_editor(
        session_df[['Student', 'is_present']],
        column_config={
            'Student': st.column_config.TextColumn('Student', disabled=True),
            'is_present': st.column_config.CheckboxColumn('Present'),
        },
        hide_index=True, width='stretch', key=f"session_editor_{ts_group}_{subject_code}",
    )

    changed = edited['is_present'] != session_df['is_present']
    c1, c2 = st.columns(2)
    with c1:
        if st.button('Save changes', type='primary', width='stretch', disabled=not changed.any(), icon=':material/save:'):
            try:
                now_present = session_df.loc[changed & edited['is_present'], 'log_id'].tolist()
                now_absent = session_df.loc[changed & ~edited['is_present'], 'log_id'].tolist()
                set_attendance_status(now_present, True)
                set_attendance_status(now_absent, False)
                st.toast('Attendance updated')
                st.rerun()
            except Exception:
                st.error("Couldn't save the changes. Please try again.")
    with c2:
        st.download_button(
            'Download this session (CSV)', data=attendance_csv(session_df),
            file_name=f"attendance_{subject_code}_{ts_group[:10]}.csv", mime='text/csv',
            icon=':material/download:', type='tertiary', width='stretch',
        )


def attendance_csv(df):
    export = df.assign(Status=df['is_present'].map({True: 'Present', False: 'Absent'}))
    export = export.sort_values(by=['ts_group', 'Subject', 'Student'])[['Time', 'Subject', 'Subject Code', 'Student', 'Status']]
    # utf-8-sig so Excel shows names with non-English characters correctly
    return export.to_csv(index=False).encode('utf-8-sig')


def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role ='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    

    return False
def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Teacher login', text_alignment='center')
    st.space()
    st.space()


    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            # Slow down password guessing: lock the form briefly after repeated failures
            locked_until = st.session_state.get('login_locked_until', 0)
            if time.time() < locked_until:
                st.error(f"Too many failed attempts. Try again in {int(locked_until - time.time()) + 1} seconds.")
            elif login_teacher(teacher_username.strip(), teacher_pass):
                st.session_state.login_failures = 0
                st.toast("Welcome back!", icon="👋")
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.login_failures = st.session_state.get('login_failures', 0) + 1
                if st.session_state.login_failures >= MAX_LOGIN_ATTEMPTS:
                    st.session_state.login_failures = 0
                    st.session_state.login_locked_until = time.time() + LOCKOUT_SECONDS
                    st.error(f"Too many failed attempts. Try again in {LOCKOUT_SECONDS} seconds.")
                else:
                    st.error("Incorrect username or password.")

    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()



def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    teacher_username, teacher_name = teacher_username.strip(), teacher_name.strip()
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "Please fill in all the fields."
    if ' ' in teacher_username:
        return False, "Usernames can't contain spaces."
    if len(teacher_pass) < MIN_PASSWORD_LENGTH:
        return False, f"Your password must be at least {MIN_PASSWORD_LENGTH} characters long."
    if check_teacher_exists(teacher_username):
        return False, "That username is already taken."
    if teacher_pass != teacher_pass_confirm:
        return False, "The passwords don't match."
    
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Account created. You can log in now."
    except Exception as e:
        return False, "Couldn't create your account. Please try again."
    

def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()



    st.header('Create your teacher account')

    st.space()
    st.space()

    
    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder=f"At least {MIN_PASSWORD_LENGTH} characters")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password again")

    st.caption(f"By creating an account you agree to the [Privacy Policy]({PRIVACY_URL}).")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)


    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()