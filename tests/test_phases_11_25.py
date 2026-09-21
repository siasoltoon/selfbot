from datetime import datetime, timezone
import asyncio
import pytest
from selfbot.db import Database
from selfbot.domain_store import DomainStore
from selfbot.services import CoreServices
from selfbot.ocr import OCRBenchmark, OCRCase
from selfbot.adversarial import AdversarialHarness, DEFAULT_MATH_FAILURE_CASES
from selfbot.ux import UXMessage, UXValidator
from selfbot.release import default_release_audit, EvidenceStatus, ReleaseAudit, EvidenceItem

def test_phase11_20_services_are_composed(tmp_path):
    db=Database(f"sqlite:///{tmp_path/'x.db'}"); db.create_schema_for_tests()
    services=CoreServices.create(db,owner_id="owner")
    assert services.admin is not None and services.security is not None
    assert services.domain_store is not None
    record=services.domain_store.put("reminder",{"text":"hello"},owner_id="owner")
    assert services.domain_store.get(record).state["text"]=="hello"

class EchoOCR:
    async def recognize(self,image):
        return image.decode()

def test_phase21_ocr_benchmark_is_measured():
    report=asyncio.run(OCRBenchmark(EchoOCR()).run([OCRCase("1",b"x+1","x+1","x+1","x")]))
    assert report.metrics.samples==1
    assert report.metrics.character_accuracy==1.0
    assert report.metrics.problem_reconstruction_accuracy==1.0

def test_phase22_adversarial_harness_never_fabricates_success():
    seen=[]
    def handler(value):
        seen.append(value)
        if value=="1/0": raise ZeroDivisionError()
    results=AdversarialHarness(handler).run(DEFAULT_MATH_FAILURE_CASES)
    assert len(results)==len(DEFAULT_MATH_FAILURE_CASES)
    assert all(r.handled and r.safe for r in results)

def test_phase23_ux_validation_and_pagination():
    validator=UXValidator()
    validator.validate(UXMessage("سلام",language="fa",rtl=True))
    pages=validator.paginate("x"*200,100)
    assert len(pages)==2

def test_phase25_release_audit_does_not_claim_unrun_evidence():
    audit=default_release_audit()
    assert not audit.passed
    assert "deployment" in audit.missing()
    assert audit.items[0].status is EvidenceStatus.NOT_RUN

def test_phase24_release_evidence_requires_all_items():
    audit=ReleaseAudit((EvidenceItem("security",EvidenceStatus.PASS),EvidenceItem("deployment",EvidenceStatus.BLOCKED)))
    assert audit.blocked and not audit.passed
