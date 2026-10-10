# Security Policy

ClassTrack AI stores biometric data (face and voice embeddings), so we take security reports seriously.

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report it privately through GitHub instead:
[**Report a vulnerability**](https://github.com/adididev/ClassTrack-AI/security/advisories/new)

Include what you found, how to reproduce it, and the impact you expect. We aim to reply within 7 days.

## How data is protected

- Face and voice data are stored only as numeric embeddings; photos and recordings are not saved.
- Teacher passwords are hashed with bcrypt.
- Every database table has Row Level Security enabled with no public policies, so only the server-side key can read or write data.
- The Supabase key is read from environment variables or `.streamlit/secrets.toml`, which is git-ignored. Never commit it.

## Known limitations

- Face login has no liveness detection, so a photo of a student could be used to log in as them.
- Login lockout after failed password attempts is per browser session.
