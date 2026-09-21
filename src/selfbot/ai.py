"""Provider-neutral AI and long-term memory services."""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Protocol
from .errors import ValidationError
class AIProvider(Protocol):
    async def generate(self,prompt:str,context:tuple[str,...]=())->str: ...
@dataclass(frozen=True,slots=True)
class MemoryItem:
    memory_id:str
    owner_id:str
    category:str
    content:str
    permission:str="owner"
@dataclass(slots=True)
class MemoryStore:
    items:dict[str,MemoryItem]=field(default_factory=dict)
    def save(self,item:MemoryItem)->None:
        if not item.content.strip(): raise ValidationError("memory content is empty")
        self.items[item.memory_id]=item
    def search(self,owner_id:str,query:str)->tuple[MemoryItem,...]:
        q=query.lower().strip()
        return tuple(x for x in self.items.values() if x.owner_id==owner_id and q in x.content.lower())
    def update(self,memory_id:str,content:str)->None:
        if memory_id not in self.items: raise ValidationError("memory not found")
        if not content.strip(): raise ValidationError("memory content is empty")
        old=self.items[memory_id]; self.items[memory_id]=MemoryItem(old.memory_id,old.owner_id,old.category,content,old.permission)
    def forget(self,memory_id:str)->None: self.items.pop(memory_id,None)
@dataclass(slots=True)
class AIRouter:
    provider:AIProvider
    memory:MemoryStore
    async def chat(self,owner_id:str,prompt:str)->str:
        if not prompt.strip(): raise ValidationError("prompt is empty")
        context=tuple(x.content for x in self.memory.search(owner_id,prompt)[:8])
        return await self.provider.generate(prompt,context)
    async def summarize(self,text:str)->str:
        if not text.strip(): raise ValidationError("text is empty")
        return await self.provider.generate("Summarize:\n"+text)
    async def translate(self,text:str,target_language:str)->str:
        if not text.strip() or not target_language.strip(): raise ValidationError("translation input is incomplete")
        return await self.provider.generate("Translate to "+target_language+":\n"+text)
