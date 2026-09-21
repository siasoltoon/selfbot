import asyncio
from dataclasses import dataclass
import pytest
from selfbot.ai import AIRouter,MemoryItem,MemoryStore
from selfbot.automation import AutomationEngine,AutomationRule,ContentStore,SavedContent
from selfbot.errors import AuthorizationError,ConflictError,ValidationError
from selfbot.games import GameEngine
from selfbot.telegram_core import SelfBotService
from selfbot.voice import VoiceService
from selfbot.worker import JobStatus,WorkerCapabilities,WorkerJob,WorkerRegistry,WorkerRuntime
from selfbot.events import EventEnvelope

class FakeTelegram:
    async def get_me(self): return {"id":"1"}
    async def update_profile(self,**fields): return fields
    async def block_user(self,user_id): return {"blocked":str(user_id)}

def test_selfbot_owner_boundary():
    service=SelfBotService(FakeTelegram(),"owner")
    assert asyncio.run(service.ping())=="pong"
    with pytest.raises(AuthorizationError): asyncio.run(service.identity("other"))
    assert asyncio.run(service.identity("owner"))=={"id":"1"}

def test_automation_keyword_and_cooldown():
    seen=[]
    async def action(event): seen.append(event.event_id); return "ok"
    engine=AutomationEngine()
    engine.add(AutomationRule("r","telegram.new_message",action,keyword="hello",cooldown_seconds=10))
    event=EventEnvelope("telegram.new_message","test",{"text":"hello"})
    assert asyncio.run(engine.handle(event,100))==["ok"]
    assert asyncio.run(engine.handle(event,105))==[]
    assert len(seen)==1

def test_content_and_game_boundaries():
    store=ContentStore(); store.save(SavedContent("1","text","Hello World",("greeting",)))
    assert store.search("hello")[0].content=="Hello World"
    assert ContentStore.format_text("x","bold")=="**x**"
    game=GameEngine(); assert game.award("u",10)==10
    assert game.buy("u",4)==6
    with pytest.raises(ConflictError): game.buy("u",99)

class Provider:
    async def generate(self,prompt,context=()): return prompt+"|"+str(len(context))

def test_ai_memory_router():
    memory=MemoryStore(); memory.save(MemoryItem("1","u","fact","likes python"))
    assert memory.search("u","python")
    router=AIRouter(Provider(),memory)
    assert asyncio.run(router.chat("u","python")).endswith("|1")
    memory.update("1","likes testing"); memory.forget("1"); assert not memory.search("u","testing")

class STT:
    async def transcribe(self,audio,language=None): return "hello"
class TTS:
    async def synthesize(self,text,voice=None): return text.encode()

def test_voice_boundaries():
    service=VoiceService(STT(),TTS())
    assert asyncio.run(service.transcribe(b"x"))=="hello"
    assert asyncio.run(service.speak("hi"))==b"hi"
    with pytest.raises(ValidationError): asyncio.run(service.transcribe(b""))

def test_worker_auth_capability_execution_and_cancel():
    registry=WorkerRegistry("secret")
    runtime=WorkerRuntime(registry,"pc","secret",WorkerCapabilities(frozenset({"echo"}),4,False))
    runtime.register_handler("echo",lambda payload: payload["value"])
    job=asyncio.run(runtime.execute(WorkerJob("j","echo",{"value":3})))
    assert job.status is JobStatus.SUCCEEDED and job.result=={"value":3}
    runtime.cancel("j2")
    cancelled=asyncio.run(runtime.execute(WorkerJob("j2","echo",{"value":3})))
    assert cancelled.status is JobStatus.CANCELLED
    with pytest.raises(AuthorizationError): registry.authenticate("bad")
