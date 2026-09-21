"""Phase 11-20 core capability tests."""
from datetime import datetime, timezone
import asyncio
import pytest
from selfbot.admin import AdminService
from selfbot.learning import LearningEngine, LearningObservation, LearningSuggestion
from selfbot.workflows import WorkflowEngine, Workflow
from selfbot.events import EventEnvelope
from selfbot.reminders import ReminderService, ReminderStatus
from selfbot.security import SecurityService
from selfbot.backup import BackupService
from selfbot.analytics import Analytics
from selfbot.storage import StorageService, StoredItem
from selfbot.agents import AgentRouter, AgentRoute
from selfbot.hardening import StoragePolicy, validate_storage_policy
from selfbot.errors import AuthorizationError, ValidationError

def test_admin_owner_gate():
    service=AdminService("owner")
    with pytest.raises(AuthorizationError): service.snapshot("other",bot={},tasks={},workers={},plugins=())
    assert service.snapshot("owner",bot={},tasks={},workers={},plugins=()).bot == {}

def test_learning_requires_approval():
    e=LearningEngine()
    e.observe(LearningObservation("command","/ping"))
    e.suggest(LearningSuggestion("s1","automation","suggest auto reply"))
    assert e.summarize()["command"]==1
    assert e.approve("s1").requires_approval is False

@pytest.mark.asyncio
async def test_workflow_condition_and_action():
    seen=[]
    engine=WorkflowEngine()
    engine.add(Workflow("w1","message",lambda e:"ok" in str(e.payload.get("text")),lambda e:seen.append(e.event_id)))
    event=EventEnvelope("message","test",{"text":"ok"})
    result=await engine.handle(event)
    assert result[0].executed and seen

def test_reminder_lifecycle():
    service=ReminderService()
    item=service.create("u","test",datetime.now(timezone.utc))
    service.complete("u",item.reminder_id)
    assert service.list("u")[0].status is ReminderStatus.COMPLETED

def test_emergency_lock_preserves_owner_recovery():
    s=SecurityService("owner")
    s.grant_trusted("trusted")
    s.emergency_lock("owner")
    with pytest.raises(AuthorizationError): s.authorize("trusted")
    s.unlock("owner")
    s.authorize("trusted")

def test_backup_checksum_and_sections():
    service=BackupService()
    body,manifest=service.export({"settings":{"x":1},"memory":[]},created_at="now")
    assert service.validate(body,manifest)["settings"]["x"]==1
    with pytest.raises(ValidationError): service.validate(body+b"x",manifest)

def test_analytics_snapshot():
    a=Analytics()
    a.increment("commands",2); a.observe_duration("task",1.0); a.observe_duration("task",3.0)
    assert a.snapshot()["counters"]["commands"]==2
    assert a.snapshot()["durations"]["task"]["avg"]==2.0

def test_storage_owner_scope_and_archive():
    s=StorageService()
    s.save(StoredItem("i","u","Notes","document",("python",),"study"))
    assert len(s.search("u","python"))==1
    s.archive("u","i")
    assert s.search("u","python")==()

class EchoAgent:
    async def run(self,prompt,context=()):
        return prompt

@pytest.mark.asyncio
async def test_agent_router_permission_boundary():
    r=AgentRouter(); r.register(AgentRoute("research","agent.research"),EchoAgent())
    with pytest.raises(AuthorizationError): await r.run("research","hello",allowed_permissions=set())
    assert await r.run("research","hello",allowed_permissions={"agent.research"})=="hello"

def test_hardening_policy():
    validate_storage_policy(StoragePolicy())
    with pytest.raises(ValidationError): validate_storage_policy(StoragePolicy(max_payload_bytes=1))
