"""Advanced automation workflow primitives: EVENT -> CONDITION -> ACTION -> LOG."""
from __future__ import annotations
import inspect
from dataclasses import dataclass
from typing import Any, Awaitable, Callable
from .events import EventEnvelope
from .errors import ValidationError

Condition = Callable[[EventEnvelope], bool | Awaitable[bool]]
Action = Callable[[EventEnvelope], Any | Awaitable[Any]]

@dataclass(frozen=True, slots=True)
class Workflow:
    workflow_id: str
    event_type: str
    condition: Condition
    action: Action
    enabled: bool = True

@dataclass(frozen=True, slots=True)
class WorkflowResult:
    workflow_id: str
    executed: bool
    result: Any = None
    error: str | None = None

class WorkflowEngine:
    def __init__(self) -> None:
        self._items: dict[str, Workflow] = {}
    def add(self, workflow: Workflow) -> None:
        if not workflow.workflow_id.strip() or not workflow.event_type.strip(): raise ValidationError("workflow identifiers are required")
        if workflow.workflow_id in self._items: raise ValidationError("workflow already exists")
        self._items[workflow.workflow_id] = workflow
    async def handle(self, event: EventEnvelope) -> tuple[WorkflowResult, ...]:
        out: list[WorkflowResult] = []
        for item in tuple(self._items.values()):
            if not item.enabled or item.event_type != event.event_type: continue
            try:
                condition = item.condition(event)
                if inspect.isawaitable(condition): condition = await condition
                if not condition:
                    out.append(WorkflowResult(item.workflow_id, False))
                    continue
                result = item.action(event)
                if inspect.isawaitable(result): result = await result
                out.append(WorkflowResult(item.workflow_id, True, result))
            except Exception as exc:
                out.append(WorkflowResult(item.workflow_id, False, error=type(exc).__name__))
        return tuple(out)
