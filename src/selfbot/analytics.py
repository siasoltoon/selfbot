"""Small analytics/monitoring aggregation boundary."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
from statistics import mean

@dataclass(slots=True)
class Analytics:
    counters: Counter[str] = field(default_factory=Counter)
    durations: dict[str,list[float]] = field(default_factory=dict)
    def increment(self, name: str, amount: int = 1) -> None:
        self.counters[name] += amount
    def observe_duration(self, name: str, seconds: float) -> None:
        self.durations.setdefault(name, []).append(max(0.0, float(seconds)))
    def snapshot(self) -> dict[str, object]:
        return {"counters":dict(self.counters),"durations":{k:{"count":len(v),"avg":mean(v) if v else 0.0,"max":max(v) if v else 0.0} for k,v in self.durations.items()}}
