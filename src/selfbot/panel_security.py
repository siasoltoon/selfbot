"""Authenticated compact tokens for the Telegram capability panel."""
from __future__ import annotations
import base64
import hashlib
import hmac


class PanelTokenSigner:
    def __init__(self, secret: str) -> None:
        self._key = hashlib.sha256(secret.encode("utf-8")).digest()

    def issue(self, owner_id: str) -> str:
        payload = owner_id.strip().encode("utf-8")
        signature = hmac.new(self._key, payload, hashlib.sha256).digest()[:12]
        raw = payload + b"." + signature
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    def verify(self, token: str) -> str | None:
        try:
            padded = token + "=" * (-len(token) % 4)
            raw = base64.urlsafe_b64decode(padded.encode("ascii"))
            if len(raw) <= 13 or raw[-13:-12] != b".":
                return None
            payload, signature = raw[:-13], raw[-12:]
            expected = hmac.new(self._key, payload, hashlib.sha256).digest()[:12]
            if not hmac.compare_digest(signature, expected):
                return None
            owner_id = payload.decode("utf-8").strip()
            return owner_id or None
        except (ValueError, UnicodeDecodeError):
            return None
