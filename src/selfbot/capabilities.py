"""Durable per-owner capability registry and feature gates."""
from __future__ import annotations
from dataclasses import dataclass
from .domain_store import DomainStore
from .errors import NotFoundError, ValidationError


@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    capability_id: str
    title: str
    description: str
    default_enabled: bool = False
    toggleable: bool = True


CAPABILITIES: tuple[CapabilityDefinition, ...] = (
    CapabilityDefinition("ai", "هوش مصنوعی", "دستیار، گفت‌وگو، خلاصه‌سازی و ترجمه"),
    CapabilityDefinition("memory", "حافظه بلندمدت", "ذخیره، جست‌وجو، به‌روزرسانی و حذف حافظه"),
    CapabilityDefinition("voice", "دستیار صوتی", "STT/TTS و فرمان‌های صوتی"),
    CapabilityDefinition("web", "هوش وب", "تحقیق و دریافت امن اطلاعات وب"),
    CapabilityDefinition("plugins", "اکوسیستم Plugin", "افزونه‌های مستقل و قابل جایگزینی"),
    CapabilityDefinition("worker", "PC Worker", "پردازش سنگین اختیاری روی Worker"),
    CapabilityDefinition("automation", "اتوماسیون پیشرفته", "رویداد، شرط، اقدام، اجرا و لاگ"),
    CapabilityDefinition("reminders", "یادآورها", "یادآورهای یک‌باره و تکرارشونده"),
    CapabilityDefinition("backup", "Backup & Restore", "پشتیبان‌گیری و بازیابی اعتبارسنجی‌شده"),
    CapabilityDefinition("analytics", "Analytics", "تحلیل فعالیت، خطا و عملکرد"),
    CapabilityDefinition("learning", "یادگیری کنترل‌شده", "پیشنهاد و یادگیری بدون تغییر خاموش رفتار حساس"),
    CapabilityDefinition("multi_agent", "Multi-Agent AI", "نقش‌های تخصصی پشت یک Router مشترک"),
    CapabilityDefinition("ocr", "OCR", "تشخیص متن از تصویر و سند"),
    CapabilityDefinition("tasks", "Task & Scheduler", "وظیفه، صف و زمان‌بندی پایدار", True, False),
    CapabilityDefinition("security", "Security", "مجوز، ممیزی و قفل اضطراری", True, False),
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
                {"enabled": {item.capability_id: item.default_enabled for item in CAPABILITIES}},
                owner_id=owner,
            )
            return self.store.get(record_id)

    def definition(self, capability_id: str) -> CapabilityDefinition:
        value = str(capability_id).strip().lower()
        for item in CAPABILITIES:
            if item.capability_id == value:
                return item
        raise NotFoundError(f"unknown capability: {capability_id}")

    def is_enabled(self, owner_id: str, capability_id: str) -> bool:
        definition = self.definition(capability_id)
        state = self._record(owner_id).state
        return bool(state.get("enabled", {}).get(definition.capability_id, definition.default_enabled))

    def set_enabled(self, owner_id: str, capability_id: str, enabled: bool) -> bool:
        definition = self.definition(capability_id)
        if not definition.toggleable and bool(enabled) != definition.default_enabled:
            raise ValidationError(f"capability cannot be disabled: {definition.capability_id}")
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
        return {
            item.capability_id: bool(enabled.get(item.capability_id, item.default_enabled))
            for item in CAPABILITIES
        }

    def require(self, owner_id: str, capability_id: str) -> None:
        if not self.is_enabled(owner_id, capability_id):
            raise ValidationError(f"capability is disabled: {self.definition(capability_id).capability_id}")
