"""Safe Telegram self-management use cases."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol
from .errors import AuthorizationError, ValidationError
class TelegramManagementPort(Protocol):
    async def get_me(self)->Any: ...
    async def update_profile(self,**fields:Any)->Any: ...
    async def block_user(self,user_id:str|int)->Any: ...
@dataclass(slots=True)
class SelfBotService:
    telegram: TelegramManagementPort
    owner_id: str
    enabled: bool=True
    def _owner(self,actor_id:str|None)->None:
        if actor_id is None or actor_id!=self.owner_id: raise AuthorizationError("owner permission required")
    async def status(self)->dict[str,bool]: return {"enabled":self.enabled}
    async def ping(self)->str: return "pong"
    async def identity(self,actor_id:str|None)->Any:
        self._owner(actor_id); return await self.telegram.get_me()
    async def set_profile(self,actor_id:str|None,**fields:Any)->Any:
        self._owner(actor_id)
        allowed={"first_name","last_name","about"}
        if set(fields)-allowed: raise ValidationError("unsupported profile field")
        if not any(v is not None for v in fields.values()): raise ValidationError("profile update is empty")
        return await self.telegram.update_profile(**fields)
    async def block(self,actor_id:str|None,user_id:str|int)->Any:
        self._owner(actor_id); return await self.telegram.block_user(user_id)
