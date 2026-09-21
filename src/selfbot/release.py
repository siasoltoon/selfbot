"""Production hardening and final release evidence model."""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
class EvidenceStatus(StrEnum): PASS="pass"; FAIL="fail"; BLOCKED="blocked"; NOT_RUN="not_run"
@dataclass(frozen=True,slots=True)
class EvidenceItem:
    name:str
    status:EvidenceStatus
    detail:str=""
@dataclass(frozen=True,slots=True)
class ReleaseAudit:
    items:tuple[EvidenceItem,...]
    @property
    def passed(self)->bool:return bool(self.items) and all(x.status is EvidenceStatus.PASS for x in self.items)
    @property
    def blocked(self)->bool:return any(x.status is EvidenceStatus.BLOCKED for x in self.items)
    def missing(self)->tuple[str,...]:return tuple(x.name for x in self.items if x.status is not EvidenceStatus.PASS)
def default_release_audit()->ReleaseAudit:
    return ReleaseAudit(tuple(EvidenceItem(x,EvidenceStatus.NOT_RUN) for x in ("architecture","code_quality","security","dependencies","tests","integration","startup_shutdown","backup_restore","performance","deployment","rollback_recovery","documentation")))
