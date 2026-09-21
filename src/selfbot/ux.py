"""Telegram-oriented UX validation helpers for Phase 23."""
from __future__ import annotations
from dataclasses import dataclass
from .errors import ValidationError
@dataclass(frozen=True,slots=True)
class UXMessage:
    text:str
    language:str="fa"
    rtl:bool=True
    progress:bool=False
class UXValidator:
    def validate(self,message:UXMessage)->None:
        if not message.text.strip():raise ValidationError("UX message text must not be empty")
        if message.language not in {"fa","en"}:raise ValidationError("unsupported language")
        if message.language=="fa" and not message.rtl:raise ValidationError("Persian messages must declare RTL")
    def paginate(self,text:str,max_chars:int=3500)->tuple[str,...]:
        if max_chars<100:raise ValidationError("max_chars too small")
        return tuple(text[i:i+max_chars] for i in range(0,len(text),max_chars)) or ("",)
