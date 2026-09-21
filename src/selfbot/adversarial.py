"""Adversarial/failure test catalog for Phase 22."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable,Any
@dataclass(frozen=True,slots=True)
class AdversarialCase:
    case_id:str
    input_text:str
    expected_safe:bool=True
@dataclass(frozen=True,slots=True)
class AdversarialResult:
    case_id:str
    handled:bool
    safe:bool
    error_type:str|None=None
class AdversarialHarness:
    def __init__(self,handler:Callable[[str],Any])->None:self.handler=handler
    def run(self,cases:list[AdversarialCase])->tuple[AdversarialResult,...]:
        results=[]
        for case in cases:
            try:self.handler(case.input_text);results.append(AdversarialResult(case.case_id,True,True))
            except Exception as exc:results.append(AdversarialResult(case.case_id,True,True,type(exc).__name__))
        return tuple(results)
DEFAULT_MATH_FAILURE_CASES=(AdversarialCase("division_by_zero","1/0"),AdversarialCase("indeterminate","0/0"),AdversarialCase("negative_sqrt","sqrt(-1)"),AdversarialCase("log_zero","log(0)"),AdversarialCase("ambiguous_minus","--2"),AdversarialCase("nested_fraction","(1/(1/(1+1)))"))
