"""Deterministic automation engine and saved content triggers."""
from __future__ import annotations
import inspect
from dataclasses import dataclass,field
from typing import Any,Awaitable,Callable
from .events import EventEnvelope
from .errors import ValidationError
Action=Callable[[EventEnvelope],Any|Awaitable[Any]]
@dataclass(frozen=True,slots=True)
class AutomationRule:
    rule_id:str
    event_type:str
    action:Action
    keyword:str|None=None
    cooldown_seconds:int=0
    enabled:bool=True
    def __post_init__(self):
        if not self.rule_id.strip() or not self.event_type.strip(): raise ValidationError("automation rule identifiers are required")
        if self.cooldown_seconds<0: raise ValidationError("cooldown_seconds must be non-negative")
@dataclass(slots=True)
class AutomationEngine:
    rules:list[AutomationRule]=field(default_factory=list)
    _last_run:dict[str,float]=field(default_factory=dict)
    def add(self,rule:AutomationRule)->None:
        if any(r.rule_id==rule.rule_id for r in self.rules): raise ValidationError("automation rule already exists")
        self.rules.append(rule)
    async def handle(self,event:EventEnvelope,now:float)->list[Any]:
        out=[]
        text=str(event.payload.get("text") or "")
        for rule in tuple(self.rules):
            if not rule.enabled or rule.event_type!=event.event_type: continue
            if rule.keyword and rule.keyword.lower() not in text.lower(): continue
            if rule.cooldown_seconds and now-self._last_run.get(rule.rule_id,-float("inf"))<rule.cooldown_seconds: continue
            result=rule.action(event)
            if inspect.isawaitable(result): result=await result
            self._last_run[rule.rule_id]=now; out.append(result)
        return out
@dataclass(frozen=True,slots=True)
class SavedContent:
    content_id:str
    kind:str
    body:str
    keywords:tuple[str,...]=()
class ContentStore:
    def __init__(self): self._items={}
    def save(self,item:SavedContent)->None:
        if item.content_id in self._items: raise ValidationError("content already exists")
        if not item.body.strip(): raise ValidationError("content body is empty")
        self._items[item.content_id]=item
    def search(self,query:str)->tuple[SavedContent,...]:
        q=query.strip().lower()
        return tuple(x for x in self._items.values() if q in x.body.lower() or any(q in k.lower() for k in x.keywords))
    @staticmethod
    def format_text(text:str,style:str)->str:
        if style=="bold": return "**"+text+"**"
        if style=="italic": return "_"+text+"_"
        if style=="mono": return "[mono]"+text+"[/mono]"
        if style=="plain": return text
        raise ValidationError("unsupported text style")
