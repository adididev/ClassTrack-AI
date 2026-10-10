-- ClassTrack AI database schema
-- Run this once in your Supabase project: Dashboard -> SQL Editor -> New query -> paste -> Run.
-- Table/column names match what the app queries in src/database/db.py and src/components/*.

create table if not exists public.teachers (
    teacher_id  bigint generated always as identity primary key,
    username    text not null unique,
    password    text not null,          -- bcrypt hash
    name        text not null,
    created_at  timestamptz not null default now()
);

create table if not exists public.students (
    student_id       bigint generated always as identity primary key,
    name             text not null,
    face_embedding   jsonb,             -- 128-d dlib face descriptor
    voice_embedding  jsonb,             -- 256-d resemblyzer voice embedding (optional)
    created_at       timestamptz not null default now()
);

create table if not exists public.subjects (
    subject_id    bigint generated always as identity primary key,
    subject_code  text not null unique, -- used in join links / QR codes
    name          text not null,
    section       text,
    teacher_id    bigint not null references public.teachers(teacher_id) on delete cascade,
    created_at    timestamptz not null default now()
);

create table if not exists public.subject_students (
    subject_id  bigint not null references public.subjects(subject_id) on delete cascade,
    student_id  bigint not null references public.students(student_id) on delete cascade,
    enrolled_at timestamptz not null default now(),
    primary key (subject_id, student_id)
);

create table if not exists public.attendance_logs (
    id          bigint generated always as identity primary key,
    student_id  bigint not null references public.students(student_id) on delete cascade,
    subject_id  bigint not null references public.subjects(subject_id) on delete cascade,
    "timestamp" timestamp not null,     -- one value per attendance session
    is_present  boolean not null default false
);

create index if not exists attendance_logs_subject_idx on public.attendance_logs(subject_id);
create index if not exists attendance_logs_student_idx on public.attendance_logs(student_id);

-- Security: the app talks to Supabase only from the server, using the service_role / secret key,
-- which bypasses RLS. Enabling RLS with no policies blocks the public anon key from reading
-- password hashes and biometric embeddings.
alter table public.teachers         enable row level security;
alter table public.students         enable row level security;
alter table public.subjects         enable row level security;
alter table public.subject_students enable row level security;
alter table public.attendance_logs  enable row level security;
