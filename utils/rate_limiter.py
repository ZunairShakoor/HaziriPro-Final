"""
A minimal in-memory rate limiter for login attempts.

Deliberately NOT a new pip dependency (Flask-Limiter, etc.) — after the
trouble with dlib/TensorFlow failing to install, this avoids introducing
another package that could break setup on some machines. It's in-memory
only, so it resets on app restart and doesn't share state across
multiple server processes — fine for a single-process dev/small
deployment, but if this app is ever run with multiple worker processes
(e.g. gunicorn -w 4), switch to a shared store (Redis, or the database)
instead.
"""

import time
from threading import Lock

MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60  # 15 minutes

_attempts = {}
_lock = Lock()


def _key(identifier):
    return identifier.strip().lower()


def is_locked_out(identifier):
    """Return remaining lockout seconds (0 if not locked out)."""
    with _lock:
        record = _attempts.get(_key(identifier))
        if not record:
            return 0

        count, locked_until = record
        if locked_until and locked_until > time.time():
            return int(locked_until - time.time())

        return 0


def record_failed_attempt(identifier):
    """Record a failed login attempt; locks out after MAX_ATTEMPTS."""
    with _lock:
        key = _key(identifier)
        count, locked_until = _attempts.get(key, (0, None))
        count += 1

        if count >= MAX_ATTEMPTS:
            locked_until = time.time() + LOCKOUT_SECONDS
        else:
            locked_until = None

        _attempts[key] = (count, locked_until)


def clear_attempts(identifier):
    """Call this on a successful login to reset the counter."""
    with _lock:
        _attempts.pop(_key(identifier), None)
