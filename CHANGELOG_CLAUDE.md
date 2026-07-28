# Changes made by Claude

This file documents everything that was changed from the original repo. Nothing
in this list required changing your database schema by hand — just run
`flask db migrate` / `flask db upgrade` (or `python init_db.py` on a fresh DB)
after pulling these changes, since one new table (`notifications`) was added.

## Bug fixes

- **`routes/employees.py`** — the employee search (`?search=...`) called
  `db.or_(...)` without importing `db`, so searching crashed with a
  `NameError`. Added the missing import.
- **Circular import pattern** — `services/employee_service.py`,
  `services/payroll_service.py`, `services/report_service.py`,
  `routes/settings.py`, `init_db.py`, and `recreate_db.py` all imported
  `db` via `from app import db` instead of `from extensions import db`.
  This worked by luck of import order but was fragile. All now import
  from `extensions` directly.
- **`models/__init__.py`** — removed an unused, dead second
  `SQLAlchemy()` instance that nothing referenced.
- **Missing templates that caused 500 errors on visit:**
  - `leave/approvals.html` → the `/leave/approvals` route now redirects
    to the working `leave/requests.html` page instead (which already
    lists pending leaves with approve/reject actions for admin/hr/manager).
  - `attendance/reports.html`, `reports/payroll.html`,
    `reports/employees.html`, `reports/emotions.html`,
    `settings/system.html` — all created.
- **Broken `url_for()` references in `templates/errors/404.html`** — it
  linked to `dashboard.admin_dashboard` and `dashboard.hr_dashboard`,
  neither of which exist (the real endpoints are `dashboard.admin` and
  `dashboard.hr`). This meant hitting a 404 as an admin/HR user actually
  crashed with a 500. Simplified to always link to `dashboard.index`.
- **Missing dependency** — `reportlab` is used for PDF generation but was
  missing from `requirements.txt`. Added `reportlab==4.2.5`.
- **Currency formatting** — the app mixed `$` and PKR. The `currency`
  Jinja filter, `utils/helpers.format_currency`, the payslip PDF, and
  every hardcoded `${{ ... }}` in the payroll templates now consistently
  show `Rs.`.
- Removed dead/unreachable code at the end of
  `services/employee_service.py` (stray `...` assignments after a
  `return`).
- Added a real `#themeToggle` / `#themeIcon` button to the navbar — the
  dark-mode CSS/JS built earlier had nothing in the actual markup to
  trigger it.
- **Face registration crash: `[Errno 2] No such file or directory:
  'uploads/faces/...'`.** `utils/helpers.save_uploaded_file()` saves the
  file to an absolute path under `static/uploads/...`, but only returned
  a path relative to the `static/` folder (correct for
  `url_for('static', filename=...)`, but missing the `static/` segment
  for direct filesystem access). `register_face()` was passing that
  same relative path straight into `Image.open()`, which needs a real
  path on disk — hence "no such file". `save_uploaded_file` now returns
  `(relative_path, absolute_path)`; the relative one is still used for
  `photo_path`/`face_encoding_path` (and therefore `url_for('static', ...)`
  in templates), and the absolute one is passed to face_recognition.
- **Dashboard stat cards looked unstyled.** The templates
  (`dashboard/admin.html`, `dashboard/employee.html`) put Bootstrap's
  `.text-white` class on the same cards we re-themed with a pale
  gradient. `.text-white` ships with `!important` in Bootstrap, so it
  silently forced the card labels and icons back to white — which
  washed out to near-invisible against the new light background (the
  big number was fine since it had its own explicit rule). Added
  `!important` overrides in `style.css` so labels/icons/numbers inside
  these cards are always dark ink, regardless of the `.text-white` class
  still being present in the markup.

## New feature: Notifications

- **`models/notification.py`** — new `Notification` model
  (title, message, category, icon, link, is_read, created_at).
- **`services/notification_service.py`** — helpers to notify a single
  user or fan out to every user in a set of roles, plus read/unread
  helpers.
- **`routes/notifications.py`** — bell dropdown JSON endpoints
  (`/recent`, `/unread-count`, mark-read, mark-all-read) and a full
  `/notifications/` list page. Registered in `app.py`.
- **Triggers wired in:**
  - New leave request → notifies admin/hr/manager.
  - Leave approved/rejected → notifies the employee.
  - New employee added → notifies admin/hr.
  - Late check-in → notifies admin/hr/manager.
  - Manually marked absent → notifies admin/hr.
- **UI** — bell icon + unread badge in the navbar, dropdown list
  (polls every 30s), "mark all read", and a full notifications page.
  Styled to match the site's aesthetic in both light and dark mode.

## Dark mode carried over

This project's zip didn't include the dark/light theme work done earlier
in our conversation. Since it's the same app, `static/css/style.css`,
`static/js/main.js`, and `templates/layouts/base.html` were merged in so
dark mode is actually usable (see the bug fix above about the missing
toggle button).

## Chatbot fix

- **Chatbot ignored the employee ID you typed in.** `routes/chatbot.py`
  always resolved "who's asking" from the logged-in account's linked
  `Employee` record — it never looked at the actual chat message. So
  when the bot said "please provide your employee ID" and you typed it
  in, that text was just checked against keywords like
  "attendance"/"leave"/"salary" (an ID matches none of them), and fell
  through to "I'm not sure I understand."
  - `services/chatbot_service.py` now recognizes an `EMP######` pattern
    in the message itself, looks up that employee, and either answers
    directly (if the same message also stated what you wanted) or asks
    what you'd like to know.
  - `routes/chatbot.py` now remembers the resolved ID in the Flask
    session, so you only have to provide it once per session — not on
    every single message.
  - This mainly matters for accounts with no personal `Employee` record
    linked (e.g. an admin/HR login testing the assistant on someone
    else's behalf). A regular employee's own account still resolves
    automatically and never needs to type an ID at all.

## Dashboard charts

Added real charts to the Admin and HR dashboards (previously the HR
dashboard had none at all, and the admin one only had a single
attendance donut):

- **This week's attendance trend** — stacked bar chart of present/late/
  absent for each of the last 7 days.
- **Emotion analytics (last 30 days)** — pie chart of every detected
  emotion from face-recognition check-in/check-out, via a new
  `services/analytics_service.py`. Shows a friendly empty-state message
  if no emotions have been recorded yet instead of an empty chart.
- **Employees by department** (admin only) — horizontal bar chart.
- **Payroll trend, last 6 months** (admin only) — line chart of total
  net payroll paid out per month.
- **Recent hires table** (HR dashboard) — this data was already being
  fetched by the route (`recent_hires`) but never actually shown in the
  template; it's now displayed.

All charts use the same color palette as the rest of the redesigned UI
(the dusty indigo/sage/amber/rose/teal tones), so they match in both
light and dark mode.

## Emotion detection bug: always showing "Neutral"

Root cause: emotion detection was analyzing the **entire webcam frame**
(background, desk, whatever else was in shot) instead of a tight crop
of just the face. DeepFace is known to bias toward "neutral" when it
has to search a whole scene rather than being handed an isolated face.

Fixed by adding `FaceRecognitionSystem.get_face_location()`, which reuses
the face-location detection that already runs during face verification.
`AttendanceService` now crops tightly to the detected face (with a small
margin) before handing the image to `EmotionDetector.detect_emotion()`,
in both check-in and check-out.

## Security pass

- **CSRF protection** — added `Flask-WTF`'s `CSRFProtect` (wired in
  `extensions.py`/`app.py`). Every one of the 23 POST forms across 16
  templates got a hidden `csrf_token` field, and every `fetch()` POST
  call (notifications, chatbot, live attendance check-in/out) now sends
  the token via an `X-CSRFToken` header, read from a new meta tag in
  `base.html` via a `getCsrfToken()` helper in `main.js`.
- **`SECRET_KEY` warning** — `app.py` now prints a loud warning on
  startup if the insecure default from `config.py` is still in use.
- **Login rate limiting** — `utils/rate_limiter.py` (new, in-memory,
  no new dependency) locks out a username for 15 minutes after 5 failed
  login attempts. Wired into `routes/auth.py`.
- **Password validation actually wired up** — `utils/validators.py`
  already had a `validate_password()` function checking length/upper/
  lower/digit requirements, but nothing in the app ever called it.
  Now used on registration (`routes/auth.py`) and on the profile
  password-change form (`routes/settings.py`).

## Audit log (new)

- `models/audit_log.py`, `services/audit_service.py` — records who did
  what, when, to what record.
- Hooked into: employee create/salary-edit/delete
  (`services/employee_service.py`), leave approve/reject
  (`routes/leave.py`), payroll approve/mark-paid
  (`services/payroll_service.py`), department delete
  (`routes/departments.py`).
- Viewable at Settings → System → "View Audit Log" (admin only):
  `routes/settings.py` + `templates/settings/audit_log.html`.

## Pagination (new)

Added to the three lists most likely to grow large over time, all
preserving existing filters in the page links:
- Employees list (`routes/employees.py` + `templates/employees/list.html`)
- Attendance history (`routes/attendance.py` + `templates/attendance/history.html`)
- Notifications (`routes/notifications.py` + `templates/notifications/list.html`,
  plus a new `NotificationService.get_paginated()`)

## Automatic absentee detection (new, CLI command)

`app.py` now registers a Flask CLI command:

```
python -m flask --app app mark-absentees
```

It marks any active employee with no attendance record for the day as
"absent" and notifies admin/hr. **This does not run automatically** —
there's no background scheduler in this project. Run it manually, or
set up a daily Windows Task Scheduler entry (or cron job on
Linux/Mac) to run it once after work hours. Optional `--date YYYY-MM-DD`
to run it for a specific day instead of today.

## Deferred (not done in this pass)

To keep everything above properly done rather than everything
half-done, these from the original list are still outstanding:
- Per-leave-type balance tracking with carryover (currently still a
  flat hardcoded 20-day allowance)
- Forgot-password / email flow (Flask-Mail is installed but unused)
- QR/barcode fallback check-in
- A real pytest test suite
- Dockerfile / docker-compose setup

Happy to tackle any of these next — just say which.


This is the important one. `app.py` registers blueprints in a loop with a
try/except — if importing a blueprint's module fails for any reason, it
just prints `✗ blueprint_name: <error>` to the console and moves on,
**silently leaving that blueprint unregistered**. That means every
`url_for()` call to any of its routes then throws a `BuildError`
("Could not build url for endpoint...") — which is confusing, because
the error you see has nothing to do with the actual root cause.

The `dashboard` blueprint imports `AttendanceService`, which imports
`ai/face_recognition.py` and `ai/emotion_detector.py` — and those
import `face_recognition`/`dlib` and `deepface`/`tensorflow`. These are
by far the two most failure-prone dependencies in `requirements.txt` on
Windows (dlib needs a C++ build toolchain + CMake; TensorFlow is picky
about Python version). If either failed during
`pip install -r requirements.txt`, the `dashboard` blueprint — and
therefore every single dashboard page — would break, even though
nothing about the dashboard itself actually needs face recognition.

**Fixed properly, not just patched around:**

- `ai/face_recognition.py` and `ai/emotion_detector.py` now wrap their
  `face_recognition`/`cv2`/`deepface` imports in `try/except`. If a
  package is missing, the module still imports fine, and each class
  exposes `.available = False`. The actual methods
  (`register_face`, `verify_face`, `recognize_face`, `detect_emotion`)
  return a clear "this feature is unavailable because X failed to
  install" message instead of crashing — and only when someone actually
  tries to use face recognition, not at import time.
- `routes/attendance.py` — same treatment for its direct `import cv2`
  (this one matters a lot, since `sidebar.html` links to
  `attendance.live` on *every single page* — a broken import here would
  have broken navigation on the entire site, not just one page).
- `services/face_service.py`, `ai/face_encoder.py` — same guard added
  for consistency, even though neither is currently wired into any
  route.
- Removed the leftover debug `print()` blocks in
  `routes/attendance.py`'s check-in/check-out handlers while in there.

**What this means for you concretely:** even if `dlib`/`face-recognition`
or `tensorflow`/`deepface` never successfully install on your Windows
machine, the rest of the app — dashboards, employees, departments,
payroll, leave, reports, notifications, the chatbot, settings — will
all work normally. Only the camera-based check-in/check-out and face
registration screens will show a clear "this feature is unavailable"
message instead of working, until those specific packages are
installed.

I verified this by simulating all four packages failing to import and
confirming every affected module still imports cleanly and degrades to
a friendly message rather than raising.

## Known limitations / things not done

- "Marked absent" notifications only fire when someone is *manually*
  marked absent via the HR attendance screen. There's no background job
  in this project to automatically flag employees who never checked in
  at all — that would need a scheduler (e.g. APScheduler or a cron job
  calling a small script) which doesn't exist yet. Happy to add one if
  you want it.
- I did not attempt to install/run the AI dependencies (face_recognition,
  DeepFace, TensorFlow, dlib) in this environment — no network access
  here — so face recognition and emotion detection weren't smoke-tested
  end-to-end. Everything else was checked by compiling every Python file
  and parsing every Jinja template, and by cross-checking every
  `url_for()` call in the templates against the actual registered Flask
  routes.
