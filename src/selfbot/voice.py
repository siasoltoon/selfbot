"""Provider-neutral speech recognition and text-to-speech boundaries."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from .errors import ValidationError
class SpeechToText(Protocol):
    async def transcribe(self,audio:bytes,language:str|None=None)->str: ...
class TextToSpeech(Protocol):
    async def synthesize(self,text:str,voice:str|None=None)->bytes: ...
@dataclass(slots=True)
class VoiceService:
    stt:SpeechToText
    tts:TextToSpeech
    async def transcribe(self,audio:bytes,language:str|None=None)->str:
        if not audio: raise ValidationError("audio is empty")
        return await self.stt.transcribe(audio,language)
    async def speak(self,text:str,voice:str|None=None)->bytes:
        if not text.strip(): raise ValidationError("text is empty")
        return await self.tts.synthesize(text,voice)
