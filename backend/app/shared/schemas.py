"""Shared, cross-module Pydantic schemas."""
from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard JSON error shape returned by the global exception handler."""

    error: str
    message: str
    details: Any | None = None
