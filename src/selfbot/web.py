"""Provider-neutral web intelligence boundary with safe URL retrieval."""
from __future__ import annotations
import ipaddress,socket
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from .errors import DependencyError,ValidationError
@dataclass(frozen=True,slots=True)
class WebDocument:
    url:str
    status:int
    content_type:str
    text:str
def _validate_url(url:str)->None:
    p=urlparse(url)
    if p.scheme!="https" or not p.hostname: raise ValidationError("only HTTPS URLs are allowed")
    try:
        ip=ipaddress.ip_address(socket.gethostbyname(p.hostname))
        if ip.is_private or ip.is_loopback or ip.is_link_local: raise ValidationError("private/local destinations are blocked")
    except socket.gaierror as exc: raise DependencyError("host resolution failed",retryable=True) from exc
class WebClient:
    def __init__(self,timeout:float=10.0): self.timeout=timeout
    def fetch(self,url:str,max_bytes:int=2_000_000)->WebDocument:
        _validate_url(url)
        if max_bytes<=0: raise ValidationError("max_bytes must be positive")
        req=Request(url,headers={"User-Agent":"selfbot/1.0"})
        try:
            with urlopen(req,timeout=self.timeout) as response:
                data=response.read(max_bytes+1)
                if len(data)>max_bytes: raise ValidationError("response exceeds size limit")
                return WebDocument(url,response.status,response.headers.get("content-type",""),data.decode("utf-8","replace"))
        except ValidationError: raise
        except Exception as exc: raise DependencyError("web request failed",retryable=True) from exc
class SearchProvider(Protocol):
    async def search(self,query:str)->list[WebDocument]: ...
