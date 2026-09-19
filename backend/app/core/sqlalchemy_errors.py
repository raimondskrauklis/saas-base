# backend/app/core/sqlalchemy_errors.py
"""SQLAlchemy IntegrityError helpers — Postgres unique-violation (23505)."""
from sqlalchemy.exc import IntegrityError

UNIQUE_VIOLATION_PG_CODE = "23505"


def is_unique_violation(exc: IntegrityError) -> bool:
    orig = exc.orig
    return orig is not None and getattr(orig, "pgcode", None) == UNIQUE_VIOLATION_PG_CODE
