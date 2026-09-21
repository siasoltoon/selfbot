"""Provider-neutral OCR benchmark harness for Phase 21."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from .errors import ValidationError
class OCRProvider(Protocol):
    async def recognize(self,image:bytes)->str: ...
@dataclass(frozen=True,slots=True)
class OCRCase:
    case_id:str
    image:bytes
    expected_text:str
    expected_expression:str|None=None
    structure_label:str|None=None
    category:str="general"
@dataclass(frozen=True,slots=True)
class OCRMetrics:
    character_accuracy:float
    expression_accuracy:float
    structural_accuracy:float
    problem_reconstruction_accuracy:float
    samples:int
@dataclass(frozen=True,slots=True)
class OCRBenchmarkReport:
    metrics:OCRMetrics
    cases:tuple[str,...]
class OCRBenchmark:
    def __init__(self,provider:OCRProvider)->None:self.provider=provider
    @staticmethod
    def _char_accuracy(expected:str,actual:str)->float:
        if not expected:return 1.0 if not actual else 0.0
        matches=sum(a==b for a,b in zip(expected,actual))
        return matches/max(len(expected),len(actual))
    async def run(self,cases:list[OCRCase])->OCRBenchmarkReport:
        if not cases: raise ValidationError("OCR benchmark requires labeled cases")
        ca=[];ea=[];sa=[];pa=[]
        for case in cases:
            actual=await self.provider.recognize(case.image)
            ca.append(self._char_accuracy(case.expected_text,actual))
            ea.append(1.0 if case.expected_expression is None or actual.strip()==case.expected_expression.strip() else 0.0)
            sa.append(1.0 if case.structure_label is None or case.structure_label in actual else 0.0)
            pa.append(1.0 if case.expected_text.strip()==actual.strip() else 0.0)
        m=OCRMetrics(sum(ca)/len(ca),sum(ea)/len(ea),sum(sa)/len(sa),sum(pa)/len(pa),len(cases))
        return OCRBenchmarkReport(m,tuple(c.case_id for c in cases))
