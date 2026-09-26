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
    category_id: str = "system"
    parent_id: str | None = None


CAPABILITIES: tuple[CapabilityDefinition, ...] = (
    CapabilityDefinition("ai", "هوش مصنوعی", "گفت‌وگو، خلاصه‌سازی، ترجمه و دستیار هوشمند", category_id="ai"),
    CapabilityDefinition("ai_chat", "گفت‌وگوی هوشمند", "پردازش و پاسخ‌گویی مکالمه‌ای", category_id="ai", parent_id="ai"),
    CapabilityDefinition("ai_summarize", "خلاصه‌سازی", "خلاصه‌سازی متن و گفتگو", category_id="ai", parent_id="ai"),
    CapabilityDefinition("ai_translate", "ترجمه", "ترجمه چندزبانه", category_id="ai", parent_id="ai"),
    CapabilityDefinition("ai_context", "Context Engine", "استفاده کنترل‌شده از زمینه و حافظه", category_id="ai", parent_id="ai"),

    CapabilityDefinition("memory", "حافظه بلندمدت", "مدیریت حافظه پایدار و شخصی", category_id="memory"),
    CapabilityDefinition("memory_save", "ذخیره حافظه", "ثبت اطلاعات مجاز در حافظه", category_id="memory", parent_id="memory"),
    CapabilityDefinition("memory_search", "جست‌وجوی حافظه", "بازیابی حافظه مرتبط", category_id="memory", parent_id="memory"),
    CapabilityDefinition("memory_update", "به‌روزرسانی", "اصلاح حافظه‌های موجود", category_id="memory", parent_id="memory"),
    CapabilityDefinition("memory_forget", "فراموشی / حذف", "حذف کنترل‌شده حافظه", category_id="memory", parent_id="memory"),

    CapabilityDefinition("voice", "صوت و رسانه", "STT، TTS و فرمان‌های صوتی", category_id="voice"),
    CapabilityDefinition("voice_stt", "Speech-to-Text", "تبدیل گفتار به متن", category_id="voice", parent_id="voice"),
    CapabilityDefinition("voice_tts", "Text-to-Speech", "تولید گفتار از متن", category_id="voice", parent_id="voice"),
    CapabilityDefinition("voice_commands", "فرمان صوتی", "اجرای فرمان‌های صوتی امن", category_id="voice", parent_id="voice"),

    CapabilityDefinition("web", "هوش وب", "جست‌وجو و دریافت امن اطلاعات وب", category_id="web"),
    CapabilityDefinition("web_search", "جست‌وجوی وب", "تحقیق و جست‌وجوی منابع", category_id="web", parent_id="web"),
    CapabilityDefinition("web_fetch", "دریافت صفحه", "دریافت امن صفحات HTTPS", category_id="web", parent_id="web"),
    CapabilityDefinition("web_research", "تحقیق چندمنبعی", "ترکیب منابع و ساخت پاسخ پژوهشی", category_id="web", parent_id="web"),

    CapabilityDefinition("plugins", "Plugins", "افزونه‌های مستقل و قابل جایگزینی", category_id="plugins"),
    CapabilityDefinition("plugins_load", "بارگذاری افزونه", "فعال‌سازی افزونه‌های مجاز", category_id="plugins", parent_id="plugins"),
    CapabilityDefinition("plugins_manage", "مدیریت افزونه", "نصب، فعال‌سازی و غیرفعال‌سازی افزونه‌ها", category_id="plugins", parent_id="plugins"),

    CapabilityDefinition("worker", "PC Worker", "پردازش سنگین اختیاری روی Worker", category_id="worker"),
    CapabilityDefinition("worker_compute", "محاسبات سنگین", "پردازش CPU/GPU", category_id="worker", parent_id="worker"),
    CapabilityDefinition("worker_media", "پردازش رسانه", "پردازش صوت، تصویر و رسانه", category_id="worker", parent_id="worker"),
    CapabilityDefinition("worker_download", "دانلود / پردازش فایل", "کارهای فایل‌محور سنگین", category_id="worker", parent_id="worker"),

    CapabilityDefinition("automation", "اتوماسیون", "رویداد → شرط → اقدام → اجرا → لاگ", category_id="automation"),
    CapabilityDefinition("automation_rules", "قوانین", "تعریف و مدیریت Ruleها", category_id="automation", parent_id="automation"),
    CapabilityDefinition("automation_conditions", "شرط‌ها", "کنترل شرایط اجرای Rule", category_id="automation", parent_id="automation"),
    CapabilityDefinition("automation_actions", "اقدام‌ها", "اجرای Actionهای مجاز", category_id="automation", parent_id="automation"),
    CapabilityDefinition("automation_audit", "Audit Log", "ثبت رویدادهای اتوماسیون", category_id="automation", parent_id="automation"),

    CapabilityDefinition("reminders", "یادآورها", "یادآورهای یک‌باره و تکرارشونده", category_id="automation"),
    CapabilityDefinition("reminders_oneoff", "یادآور یک‌باره", "یادآورهای زمان‌دار", category_id="automation", parent_id="reminders"),
    CapabilityDefinition("reminders_recurring", "یادآور تکرارشونده", "برنامه‌های تکراری", category_id="automation", parent_id="reminders"),

    CapabilityDefinition("tasks", "Task & Scheduler", "وظیفه، صف و زمان‌بندی پایدار", True, False, "automation"),
    CapabilityDefinition("tasks_queue", "صف وظایف", "مدیریت اجرای صف‌شده", True, False, "automation", "tasks"),
    CapabilityDefinition("tasks_scheduler", "Scheduler", "اجرای زمان‌بندی‌شده", True, False, "automation", "tasks"),
    CapabilityDefinition("tasks_retry", "Retry / Timeout", "کنترل تلاش مجدد و timeout", True, False, "automation", "tasks"),

    CapabilityDefinition("backup", "Backup & Restore", "پشتیبان‌گیری و بازیابی اعتبارسنجی‌شده", category_id="data"),
    CapabilityDefinition("backup_create", "ساخت Backup", "ایجاد نسخه پشتیبان", category_id="data", parent_id="backup"),
    CapabilityDefinition("backup_restore", "Restore", "بازیابی با اعتبارسنجی", category_id="data", parent_id="backup"),
    CapabilityDefinition("backup_export", "Export", "خروجی کنترل‌شده داده", category_id="data", parent_id="backup"),

    CapabilityDefinition("analytics", "Analytics", "تحلیل فعالیت، خطا و عملکرد", category_id="analytics"),
    CapabilityDefinition("analytics_usage", "Usage Analytics", "آمار استفاده", category_id="analytics", parent_id="analytics"),
    CapabilityDefinition("analytics_errors", "Error Analytics", "تحلیل خطاها", category_id="analytics", parent_id="analytics"),
    CapabilityDefinition("analytics_performance", "Performance", "شاخص‌های عملکرد", category_id="analytics", parent_id="analytics"),

    CapabilityDefinition("learning", "یادگیری کنترل‌شده", "پیشنهاد و یادگیری بدون تغییر خاموش رفتار حساس", category_id="analytics"),
    CapabilityDefinition("learning_suggestions", "پیشنهادها", "پیشنهادهای قابل بازبینی", category_id="analytics", parent_id="learning"),
    CapabilityDefinition("learning_updates", "یادگیری تأییدشده", "اعمال فقط پس از تأیید", category_id="analytics", parent_id="learning"),

    CapabilityDefinition("multi_agent", "Multi-Agent AI", "نقش‌های تخصصی پشت یک Router مشترک", category_id="ai"),
    CapabilityDefinition("multi_agent_routing", "Agent Routing", "مسیریابی بین Agentها", category_id="ai", parent_id="multi_agent"),
    CapabilityDefinition("multi_agent_roles", "Agent Roles", "نقش‌های تخصصی", category_id="ai", parent_id="multi_agent"),

    CapabilityDefinition("ocr", "OCR", "تشخیص متن از تصویر و سند", category_id="media"),
    CapabilityDefinition("ocr_image", "OCR تصویر", "استخراج متن از تصویر", category_id="media", parent_id="ocr"),
    CapabilityDefinition("ocr_pdf", "OCR PDF", "استخراج متن از PDF", category_id="media", parent_id="ocr"),
    CapabilityDefinition("ocr_handwriting", "دست‌خط", "پردازش دست‌خط و تصاویر سخت", category_id="media", parent_id="ocr"),

    CapabilityDefinition("security", "Security", "مجوز، ممیزی و قفل اضطراری", True, False, "security"),
    CapabilityDefinition("security_permissions", "Permissions", "کنترل دسترسی", True, False, "security", "security"),
    CapabilityDefinition("security_audit", "Security Audit", "ممیزی امنیتی", True, False, "security", "security"),
    CapabilityDefinition("security_lockdown", "Emergency Lockdown", "قفل اضطراری عملیات خطرناک", True, False, "security", "security"),
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

    def children(self, capability_id: str) -> tuple[CapabilityDefinition, ...]:
        value = self.definition(capability_id).capability_id
        return tuple(item for item in CAPABILITIES if item.parent_id == value)

    def is_enabled(self, owner_id: str, capability_id: str) -> bool:
        definition = self.definition(capability_id)
        state = self._record(owner_id).state
        enabled = state.get("enabled", {})
        if definition.parent_id and not bool(
            enabled.get(definition.parent_id, self.definition(definition.parent_id).default_enabled)
        ):
            return False
        return bool(enabled.get(definition.capability_id, definition.default_enabled))

    def set_enabled(self, owner_id: str, capability_id: str, enabled: bool) -> bool:
        definition = self.definition(capability_id)
        if not definition.toggleable and bool(enabled) != definition.default_enabled:
            raise ValidationError(f"capability cannot be disabled: {definition.capability_id}")
        record = self._record(owner_id)
        state = dict(record.state)
        enabled_state = dict(state.get("enabled", {}))
        enabled_state[definition.capability_id] = bool(enabled)
        if not enabled:
            for child in self.children(definition.capability_id):
                enabled_state[child.capability_id] = False
        elif definition.parent_id is None:
            for child in self.children(definition.capability_id):
                if child.toggleable:
                    enabled_state.setdefault(child.capability_id, child.default_enabled)
                else:
                    enabled_state[child.capability_id] = child.default_enabled
        state["enabled"] = enabled_state
        self.store.put(self.DOMAIN, state, owner_id=str(owner_id).strip(), record_id=record.id)
        return bool(enabled)

    def snapshot(self, owner_id: str) -> dict[str, bool]:
        state = self._record(owner_id).state
        enabled = state.get("enabled", {})
        return {
            item.capability_id: self.is_enabled(owner_id, item.capability_id)
            if item.parent_id
            else bool(enabled.get(item.capability_id, item.default_enabled))
            for item in CAPABILITIES
        }

    def require(self, owner_id: str, capability_id: str) -> None:
        if not self.is_enabled(owner_id, capability_id):
            raise ValidationError(f"capability is disabled: {self.definition(capability_id).capability_id}")
