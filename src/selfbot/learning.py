"""Controlled learning and suggestion primitives."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
from .errors import ValidationError

@dataclass(frozen=True, slots=True)
class LearningObservation:
    kind: str
    value: str
    success: bool = True

@dataclass(frozen=True, slots=True)
class LearningSuggestion:
    suggestion_id: str
    kind: str
    description: str
    requires_approval: bool = True

@dataclass(slots=True)
class LearningEngine:
    observations: list[LearningObservation] = field(default_factory=list)
    suggestions: dict[str, LearningSuggestion] = field(default_factory=dict)
    def observe(self, item: LearningObservation) -> None:
        if not item.kind.strip() or not item.value.strip(): raise ValidationError("learning observation is incomplete")
        self.observations.append(item)
    def summarize(self) -> dict[str, int]:
        return dict(Counter(x.kind for x in self.observations))
    def suggest(self, suggestion: LearningSuggestion) -> None:
        if not suggestion.suggestion_id.strip(): raise ValidationError("suggestion_id is required")
        self.suggestions[suggestion.suggestion_id] = suggestion
    def approve(self, suggestion_id: str) -> LearningSuggestion:
        item = self.suggestions.get(suggestion_id)
        if item is None: raise ValidationError("learning suggestion not found")
        return LearningSuggestion(item.suggestion_id, item.kind, item.description, False)
