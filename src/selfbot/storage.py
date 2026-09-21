"""Smart storage metadata/search boundary."""
from __future__ import annotations
from dataclasses import dataclass, field
from .errors import ValidationError

@dataclass(frozen=True, slots=True)
class StoredItem:
    item_id: str
    owner_id: str
    name: str
    kind: str
    tags: tuple[str, ...] = ()
    note: str = ""
    archived: bool = False

class StorageService:
    def __init__(self) -> None: self._items: dict[str, StoredItem] = {}
    def save(self, item: StoredItem) -> None:
        if not item.item_id.strip() or not item.owner_id.strip() or not item.name.strip(): raise ValidationError("storage item identifiers are required")
        if item.kind not in {"document","image","video","audio","archive","message"}: raise ValidationError("unsupported storage kind")
        if item.item_id in self._items: raise ValidationError("storage item already exists")
        self._items[item.item_id]=item
    def search(self, owner_id: str, query: str) -> tuple[StoredItem, ...]:
        q=query.strip().lower()
        return tuple(x for x in self._items.values() if x.owner_id==owner_id and not x.archived and (q in x.name.lower() or any(q in t.lower() for t in x.tags) or q in x.note.lower()))
    def archive(self, owner_id: str, item_id: str) -> None:
        item=self._items.get(item_id)
        if item is None or item.owner_id != owner_id: raise ValidationError("storage item not found")
        self._items[item_id]=StoredItem(item.item_id,item.owner_id,item.name,item.kind,item.tags,item.note,True)
