"""Encryption for long-lived Telegram sessions."""
from __future__ import annotations
from .errors import ConfigurationError, ValidationError

class SessionCipher:
    def __init__(self, key: str) -> None:
        if not key.strip():
            raise ConfigurationError("TELEGRAM_SESSION_ENCRYPTION_KEY is required")
        try:
            from cryptography.fernet import Fernet
            self._fernet = Fernet(key.encode())
        except Exception as exc:
            raise ConfigurationError("TELEGRAM_SESSION_ENCRYPTION_KEY must be a valid Fernet key") from exc

    def encrypt(self, session: str) -> str:
        if not session:
            raise ValidationError("session must not be empty")
        return self._fernet.encrypt(session.encode()).decode()

    def decrypt(self, token: str) -> str:
        if not token:
            raise ValidationError("encrypted session must not be empty")
        try:
            return self._fernet.decrypt(token.encode()).decode()
        except Exception as exc:
            raise ValidationError("Telegram session decryption failed") from exc
