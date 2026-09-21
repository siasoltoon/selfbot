"""Validated backup/restore manifest primitives."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from typing import Any
from .errors import ValidationError

@dataclass(frozen=True, slots=True)
class BackupManifest:
    version: int
    created_at: str
    sections: tuple[str, ...]
    sha256: str

class BackupService:
    def export(self, payload: dict[str, Any], *, created_at: str, version: int = 1) -> tuple[bytes, BackupManifest]:
        if version < 1 or not created_at.strip(): raise ValidationError("invalid backup metadata")
        body=json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
        digest=hashlib.sha256(body).hexdigest()
        return body, BackupManifest(version,created_at,tuple(sorted(payload)),digest)
    def validate(self, body: bytes, manifest: BackupManifest) -> dict[str, Any]:
        if hashlib.sha256(body).hexdigest()!=manifest.sha256: raise ValidationError("backup checksum mismatch")
        try: data=json.loads(body.decode())
        except (UnicodeDecodeError,json.JSONDecodeError) as exc: raise ValidationError("backup payload is invalid") from exc
        if not isinstance(data,dict): raise ValidationError("backup root must be an object")
        if tuple(sorted(data)) != manifest.sections: raise ValidationError("backup sections mismatch")
        return data
