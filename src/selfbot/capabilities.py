"""Durable per-owner capability registry and feature gates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .domain_store import DomainStore
from .errors import NotFoundError, ValidationError


@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    capability_id: str
    title: str
    description: str


CAPABILITIES: tuple[CapabilityDefinition, ...] = (
    CapabilityDefinition("ai", "هوش مصنوعی", "گفت‌وگو و پردازش هوشمند"),
    CapabilityDefinition("memory", "حافظه بلندمدت", "ذخیره، جست‌وجو و مدیریت حافظه"),
    CapabilityDefinition("web", "هوش وب", "جست‌وجو و دریافت امن اطلاعات وب"),
    CapabilityDefinition("automation", "اتوماسیون", "رویداد، شرط، اقدام و اجرای خودکار"),
    CapabilityDefinition("reminders", "یادآورها", "یادآورهای یک‌باره و تکرارشونده"),
    CapabilityDefinition("voice", "صدا", "تبدیل گفتار به متن و متن به گفتار"),
    CapabilityDefinition("ocr", "OCR", "تشخیص متن از تصویر و اسناد"),
    CapabilityDefinition("analytics", "تحلیل و آمار", "ثبت و مشاهده شاخص‌های عملکرد"),
    CapabilityDefinition("worker", "PC Worker", "پردازش‌های سنگین روی Worker اختیاری"),
    CapabilityDefinition("security", "امنیت", "کنترل دسترسی، قفل اضطراری و ممیزی"),
    CapabilityDefinition("plugins", "Plugin System", "قابلیت‌های افزونه‌ای مستقل"),
    CapabilityDefinition("learning", "یادگیری کنترل‌شده", "یادگیری و تنظیمات کنترل‌شده"),
    CapabilityDefinition("backup", "پشتیبان‌گیری", "پشتیبان‌گیری و بازیابی داده"),
    CapabilityDefinition("tasks", "Task & Scheduler", "صف، وظیفه و زمان‌بندی پایدار"),
)


class CapabilityService:
    """Persists enabled/disabled state and exposes enforcement primitives."""

    DOMAIN = "capabilities"

    def __init__(self, store: DomainStore) -> None:
        self.store = store

    @staticmethod
    def definitions() -> tuple[CapabilityDefinition, ...]:
        return CAPABILITIES

    @staticmethod
    def _validate_owner(owner_id: str) -> str:
        value = str(owner_id).strip()
        if not value:
            raise ValidationError("owner_id is required")
        return value

    def _record(self, owner_id: str):
        owner = self._validate_owner(owner_id)
        try:
            return self.store.get_by_domain(self.DOMAIN, owner)
        except NotFoundError:
            record_id = self.store.put(
                self.DOMAIN,
                {"enabled": {item.capability_id: False for item in CAPABILITIES}},
                owner_id=owner,
            )
            return self.store.get(record_id)

    def is_enabled(self, owner_id: str, capability_id: str) -> bool:
        definition = self.definition(capability_id)
        state = self._record(owner_id).state
        return bool(state.get("enabled", {}).get(definition.capability_id, False))

    def set_enabled(self, owner_id: str, capability_id: str, enabled: bool) -> bool:
        definition = self.definition(capability_id)
        record = self._record(owner_id)
        state = dict(record.state)
        enabled_state = dict(state.get("enabled", {}))
        enabled_state[definition.capability_id] = bool(enabled)
        state["enabled"] = enabled_state
        self.store.put(self.DOMAIN, state, owner_id=str(owner_id).strip(), record_id=record.id)
        return bool(enabled)

    def snapshot(self, owner_id: str) -> dict[str, bool]:
        state = self._record(owner_id).state
        enabled = state.get("enabled", {})
        return {item.capability_id: bool(enabled.get(item.capability_id, False)) for item in CAPABILITIES}

    def definition(self, capability_id: str) -> CapabilityDefinition:
        value = str(capability_id).strip().lower()
        for item in CAPABILITIES:
            if item.capability_id == value:
                return item
        raise NotFoundError(f"unknown capability: {capability_id}")

    def require(self, owner_id: str, capability_id: str) -> None:
        if not self.is_enabled(owner_id, capability_id):
            raise ValidationError(f"capability is disabled: {self.definition(capability_id).capability_id}")

    def render(self, owner_id: str) -> str:
        snapshot = self.snapshot(owner_id)
        lines = ["🤖 پنل مدیریت Selfbot", "", "وضعیت قابلیت‌ها:"]
        for item in CAPABILITIES:
            marker = "🟢" if snapshot[item.capability_id] else "⚪"
            lines.append(f"{marker} {item.title} — {'روشن' if snapshot[item.capability_id] else 'خاموش'}")
        lines.append("")
        lines.append("برای تغییر سریع از /capability <id> on|off استفاده کن.")
        return "\n".join(lines)
