"""Application error taxonomy and safe error classification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AppError(Exception):
    """Base error that can be safely classified for logs/API responses."""

    message: str
    code: str = "internal"
    retryable: bool = False
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return self.message


class ConfigurationError(AppError):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, "configuration", False, details)


class ValidationError(AppError):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, "validation", False, details)


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "authentication", False)


class AuthorizationError(AppError):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, "authorization", False)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "not_found", False)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, "conflict", False)


class DependencyError(AppError):
    def __init__(self, message: str, retryable: bool = True):
        super().__init__(message, "dependency_failure", retryable)


class AppTimeoutError(AppError):
    def __init__(self, message: str = "Operation timed out"):
        super().__init__(message, "timeout", True)


def classify_error(exc: BaseException) -> AppError:
    """Convert unknown exceptions into a safe application error."""

    if isinstance(exc, AppError):
        return exc
    return AppError("Unexpected internal error", "internal", False)
