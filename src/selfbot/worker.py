"""Authenticated optional PC Worker protocol and local execution runtime."""
from __future__ import annotations
import asyncio,inspect,secrets
from dataclasses import dataclass,field
from datetime import datetime,timezone
from enum import StrEnum
from typing import Any,Awaitable,Callable
from .errors import AuthorizationError,ValidationError
class WorkerStatus(StrEnum): OFFLINE="offline"; AVAILABLE="available"; BUSY="busy"
class JobStatus(StrEnum): QUEUED="queued"; CLAIMED="claimed"; RUNNING="running"; SUCCEEDED="succeeded"; FAILED="failed"; CANCELLED="cancelled"; TIMED_OUT="timed_out"; DEFERRED="deferred"; WORKER_OFFLINE="worker_offline"
@dataclass(frozen=True,slots=True)
class WorkerCapabilities:
    job_types:frozenset[str]=frozenset()
    cpu_cores:int=1
    gpu:bool=False
@dataclass(slots=True)
class WorkerRecord:
    worker_id:str
    token_hash:str
    capabilities:WorkerCapabilities
    status:WorkerStatus=WorkerStatus.OFFLINE
    last_heartbeat:datetime|None=None
    resources:dict[str,float]=field(default_factory=dict)
@dataclass(slots=True)
class WorkerJob:
    job_id:str
    job_type:str
    payload:dict[str,Any]
    timeout_seconds:float=300
    attempts:int=0
    max_attempts:int=1
    status:JobStatus=JobStatus.QUEUED
    result:dict[str,Any]|None=None
    error:str|None=None
class WorkerRegistry:
    def __init__(self,token:str):
        if not token: raise ValidationError("worker token is required")
        self._token=token; self._workers={}
    def authenticate(self,token:str)->None:
        if not secrets.compare_digest(token,self._token): raise AuthorizationError("worker authentication failed")
    def register(self,worker_id:str,token:str,caps:WorkerCapabilities)->WorkerRecord:
        self.authenticate(token)
        if not worker_id.strip(): raise ValidationError("worker_id is required")
        rec=WorkerRecord(worker_id,"configured",caps,WorkerStatus.AVAILABLE,datetime.now(timezone.utc))
        self._workers[worker_id]=rec; return rec
    def heartbeat(self,worker_id:str,token:str,resources:dict[str,float])->None:
        self.authenticate(token); rec=self._workers.get(worker_id)
        if rec is None: raise ValidationError("worker is not registered")
        rec.last_heartbeat=datetime.now(timezone.utc); rec.resources=dict(resources); rec.status=WorkerStatus.AVAILABLE
    def get(self,worker_id:str)->WorkerRecord:
        if worker_id not in self._workers: raise ValidationError("worker not registered")
        return self._workers[worker_id]
    def mark_offline(self,timeout_seconds:float)->list[str]:
        now=datetime.now(timezone.utc); offline=[]
        for rec in self._workers.values():
            if rec.last_heartbeat is None or (now-rec.last_heartbeat).total_seconds()>timeout_seconds:
                rec.status=WorkerStatus.OFFLINE; offline.append(rec.worker_id)
        return offline
class WorkerRuntime:
    def __init__(self,registry:WorkerRegistry,worker_id:str,token:str,capabilities:WorkerCapabilities):
        registry.authenticate(token); self.registry=registry; self.worker_id=worker_id; self.token=token; self.capabilities=capabilities; self.handlers={}; self.cancelled=set(); registry.register(worker_id,token,capabilities)
    def register_handler(self,job_type:str,handler:Callable[[dict[str,Any]],Any|Awaitable[Any]])->None: self.handlers[job_type]=handler
    async def execute(self,job:WorkerJob)->WorkerJob:
        if job.job_type not in self.capabilities.job_types or job.job_type not in self.handlers:
            job.status=JobStatus.DEFERRED; job.error="worker capability unavailable"; return job
        if job.job_id in self.cancelled: job.status=JobStatus.CANCELLED; return job
        job.status=JobStatus.RUNNING; job.attempts+=1
        try:
            result=self.handlers[job.job_type](job.payload)
            if inspect.isawaitable(result): result=await asyncio.wait_for(result,timeout=job.timeout_seconds)
            job.result={"value":result}; job.status=JobStatus.SUCCEEDED
        except asyncio.TimeoutError: job.status=JobStatus.TIMED_OUT; job.error="worker timeout"
        except asyncio.CancelledError: job.status=JobStatus.CANCELLED
        except Exception as exc: job.status=JobStatus.FAILED; job.error=type(exc).__name__
        return job
    def cancel(self,job_id:str)->None: self.cancelled.add(job_id)
