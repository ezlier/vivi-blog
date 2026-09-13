from collections.abc import Generator

from django.db import close_old_connections


def db_connection() -> Generator[None, None, None]:
    """Keep Django ORM connections healthy for FastAPI's sync handlers."""
    close_old_connections()
    try:
        yield
    finally:
        close_old_connections()
