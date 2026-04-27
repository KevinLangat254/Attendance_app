# Uni Attendance System

A secure, web-based student attendance management system built for universities. It replaces manual paper-based registers with GPS-verified and biometric-authenticated digital check-ins, ensuring students can only mark attendance when physically present in the classroom.

---

## Features

- **Biometric Login** — students register their fingerprint or face ID using WebAuthn (passkeys). The private key never leaves the device, making credential sharing impossible
- **One-Device Policy** — each student is restricted to a single registered biometric device to prevent proxy attendance through buddy registration
- **GPS Geofencing** — sessions are anchored to a GPS coordinate and radius. Attendance is rejected if the student is outside the defined area
- **Role-Based Access** — separate dashboards and permissions for Students and Lecturers
- **Session Management** — lecturers create sessions with start and end times, GPS location, and geofence radius
- **Attendance Reports** — lecturers view per-session attendance with student names, rates, and timestamps
- **Profile Photo Upload** — avatars stored in the database and displayed across all pages
- **Lecturer Override** — lecturers can reset a student's biometric in person when the student gets a new phone

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django REST Framework |
| Database | PostgreSQL |
| Frontend | HTML, CSS, JavaScript |
| Authentication | DRF Token Auth + WebAuthn (py-webauthn) |
| Location | GPS + Haversine geofencing |
| Media | Django MEDIA_ROOT |

---

## Project Structure

```
Attendance App/
├── attendance/
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views/
│       ├── __init__.py
│       ├── base_views.py        # ModelViewSets, claim/unclaim, avatar upload
│       ├── attendance_views.py  # Haversine formula, MarkAttendanceView
│       └── auth_views.py        # WebAuthn biometric endpoints
├── attendance_system/
│   ├── settings.py
│   └── urls.py
├── frontend/
│   ├── index.html               # Login page
│   ├── register.html            # Registration page
│   ├── profile.html             # Profile + biometric management
│   └── dashboard/
│       ├── student/dashboard.html
│       └── lecturer/dashboard.html
├── media/                       # Uploaded avatars
├── manage.py
└── .env
```

---

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip

---

## Installation

**1. Clone the repository**

```bash
git clone <repository-url>
cd "Attendance App"
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install django djangorestframework psycopg2-binary django-cors-headers
pip install django-filter Pillow python-dotenv py-webauthn
```

**4. Create a `.env` file in the project root**

```env
SECRET_KEY=your_django_secret_key_here
DEBUG=True
DB_NAME=attendance_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=127.0.0.1,localhost
```

**5. Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

**6. Seed programme and unit data (optional)**

```bash
python seed_mmu_data.py
python seed_mmu_units.py
```

**7. Start the server**

```bash
# Local only
python manage.py runserver

# Accessible on local network (for mobile testing)
python manage.py runserver 0.0.0.0:8000
```

Open `http://localhost:8000` in your browser.

---

## Mobile Testing with ngrok

WebAuthn requires HTTPS on mobile browsers. Use ngrok to get a free HTTPS tunnel:

**1. Download ngrok** from [https://ngrok.com/download](https://ngrok.com/download) and place `ngrok.exe` in the project root.

**2. Add your auth token**

```bash
.\ngrok.exe config add-authtoken YOUR_TOKEN_HERE
```

**3. Start Django on all interfaces**

```bash
python manage.py runserver 0.0.0.0:8000
```

**4. In a second terminal, start ngrok**

```bash
.\ngrok.exe http 8000
```

**5. Update `auth_views.py`** with the ngrok domain

```python
RP_ID     = 'abc.ngrok-free.app'
RP_ORIGIN = 'https://abc.ngrok-free.app'
```

**6. Update `ALLOWED_HOSTS` in `.env`**

```env
ALLOWED_HOSTS=127.0.0.1,localhost,abc.ngrok-free.app
```

**7. Restart Django** and share the HTTPS URL with users.

> **Note:** On the free ngrok plan the URL changes every time you restart ngrok. Update `RP_ID`, `RP_ORIGIN`, and `ALLOWED_HOSTS` each session.

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development, `False` for production |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | Database host (default `localhost`) |
| `DB_PORT` | Database port (default `5432`) |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |

---

## API Overview

All endpoints are prefixed with `/api/`. Full documentation is available in [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md).

### Authentication
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/login/` | No | Password login, returns token |
| POST | `/api/webauthn/login/begin/` | No | Step 1 of biometric login |
| POST | `/api/webauthn/login/complete/` | No | Step 2 — verify and return token |

### Core Endpoints
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/users/` | No | Register new account |
| GET | `/api/users/` | Yes | Get own profile or all users |
| GET | `/api/programs/` | No | List all programmes |
| POST | `/api/mark-attendance/` | Yes | Mark attendance with GPS |
| POST | `/api/upload-avatar/` | Yes | Upload profile photo |

### WebAuthn
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/webauthn/register/begin/` | Yes | Step 1 of biometric registration |
| POST | `/api/webauthn/register/complete/` | Yes | Step 2 — save public key |
| GET | `/api/webauthn/credentials/` | Yes | List registered devices |
| POST | `/api/webauthn/reset/{student_id}/` | Yes (Lecturer) | Reset student's biometric |

---

## Security

- **IDOR Protection** — all querysets are filtered by the authenticated user. Students cannot access other students' data.
- **Ownership Checks** — users can only modify their own profiles, enrollments, and sessions they own.
- **WebAuthn One-Device Policy** — each account is limited to one registered biometric credential.
- **Sign Count Validation** — the server tracks the credential sign count on every login. A decreasing count indicates a cloned credential and is rejected.
- **Challenge-Response** — a fresh random challenge is generated for every biometric operation, preventing replay attacks.
- **HTTPS Required** — WebAuthn only works on HTTPS or localhost. Use ngrok for mobile testing.

---

## User Roles

| Action | Student | Lecturer | Admin |
|---|---|---|---|
| Register and login | ✅ | ✅ | ✅ |
| Mark attendance | ✅ | ❌ | ✅ |
| Create sessions | ❌ | ✅ | ✅ |
| Claim / unclaim units | ❌ | ✅ | ✅ |
| View all attendance records | ❌ | ✅ | ✅ |
| Modify attendance records | ❌ | ✅ | ✅ |
| Reset student biometric | ❌ | ✅ | ✅ |
| Delete users or records | ❌ | ❌ | ✅ |

---

## WebAuthn — How It Works

### Registration (first time)
1. Student logs in with password and visits their profile page
2. Student taps **Register This Device**
3. Server generates a random challenge and returns registration options
4. Browser prompts fingerprint or face ID on the device
5. Device's secure chip generates a key pair — private key stays on device, public key sent to server
6. Server verifies the response and saves the public key to the database

### Login (subsequent visits)
1. Student enters username and taps **Login with Biometrics**
2. Server generates a new challenge
3. Browser prompts fingerprint or face ID
4. Device signs the challenge with the private key
5. Server verifies the signature using the stored public key and returns the auth token

---

## License

This project was developed as a university group project.
