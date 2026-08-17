"""
wizard.backend.main
===================
Uvicorn entry-point shim — re-exports the FastAPI app from wizard.backend.app.

The Makefile uses ``wizard.backend.main:app`` as the uvicorn target.
This shim avoids renaming app.py (which would break many imports).

Usage::

    uvicorn wizard.backend.main:app --host 127.0.0.1 --port 8013
"""
from wizard.backend.app import app  # re-export

__all__ = ["app"]
