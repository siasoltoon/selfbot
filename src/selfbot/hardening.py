"""Database/runtime hardening policies used by later migrations and services."""
from __future__ import annotations
from dataclasses import dataclass
from .errors import ValidationError

@dataclass(frozen=True, slots=True)
class StoragePolicy:
    max_payload_bytes: int = 1_048_576
    retention_days: int = 90
    require_timezone_aware_dates: bool = True

def validate_storage_policy(policy: StoragePolicy) -> None:
    if policy.max_payload_bytes < 1024: raise ValidationError("max_payload_bytes is too small")
    if policy.retention_days < 1: raise ValidationError("retention_days must be positive")
