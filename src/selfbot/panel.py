"""Professional Telegram panel domain model.

This module contains navigation metadata only; Telegram rendering remains in the
adapter so the core panel design stays deployment- and transport-agnostic.
"""
from __future__ import annotations

from dataclasses import dataclass

from .capabilities import CapabilityDefinition, CapabilityService


@dataclass(frozen=True, slots=True)
class PanelCategory:
    category_id: str
    title: str
    description: str
    capability_ids: tuple[str, ...]


PANEL_CATEGORIES: tuple[PanelCategory, ...] = (
    PanelCategory("ai", "🤖 هوش مصنوعی و Agentها", "AI، Multi-Agent و مدیریت رفتار هوشمند", ("ai", "multi_agent")),
    PanelCategory("memory", "🧠 حافظه", "حافظه بلندمدت و چرخه مدیریت آن", ("memory",)),
    PanelCategory("voice", "🎙 صدا و رسانه", "STT، TTS و پردازش صوتی", ("voice",)),
    PanelCategory("web", "🌐 Web Intelligence", "جست‌وجو، دریافت و تحقیق وب", ("web",)),
    PanelCategory("media", "🖼 OCR و اسناد", "OCR تصویر، PDF و دست‌خط", ("ocr",)),
    PanelCategory("automation", "⚙️ اتوماسیون و Tasks", "Automation، Reminders، Queue و Scheduler", ("automation", "reminders", "tasks")),
    PanelCategory("plugins", "🧩 Plugins", "افزونه‌ها و مدیریت چرخه عمر آن‌ها", ("plugins",)),
    PanelCategory("worker", "🖥 PC Worker", "پردازش سنگین، رسانه و فایل", ("worker",)),
    PanelCategory("data", "💾 داده و Backup", "Backup، Restore و Export", ("backup",)),
    PanelCategory("analytics", "📊 Analytics و Learning", "تحلیل، خطا، عملکرد و یادگیری کنترل‌شده", ("analytics", "learning")),
    PanelCategory("security", "🛡 امنیت", "Permissions، Audit و Emergency Lockdown", ("security",)),
    PanelCategory("system", "👤 حساب و سیستم", "حساب متصل، وضعیت سرویس و کنترل‌های عمومی", ()),
)


class PanelService:
    """Builds the hierarchical panel state from the durable capability registry."""

    def __init__(self, capabilities: CapabilityService) -> None:
        self.capabilities = capabilities

    @staticmethod
    def categories() -> tuple[PanelCategory, ...]:
        return PANEL_CATEGORIES

    def category(self, category_id: str) -> PanelCategory:
        value = str(category_id).strip().lower()
        for item in PANEL_CATEGORIES:
            if item.category_id == value:
                return item
        raise KeyError(f"unknown panel category: {category_id}")

    def roots(self, category_id: str) -> tuple[CapabilityDefinition, ...]:
        category = self.category(category_id)
        ids = set(category.capability_ids)
        return tuple(
            item for item in self.capabilities.definitions()
            if item.capability_id in ids
        )

    def children(self, capability_id: str) -> tuple[CapabilityDefinition, ...]:
        return self.capabilities.children(capability_id)

    def category_stats(self, owner_id: str, category_id: str) -> tuple[int, int]:
        roots = self.roots(category_id)
        snapshot = self.capabilities.snapshot(owner_id)
        enabled = sum(1 for item in roots if snapshot[item.capability_id])
        return enabled, len(roots)

    def summary(self, owner_id: str) -> tuple[int, int]:
        snapshot = self.capabilities.snapshot(owner_id)
        toggleable = [
            item for item in self.capabilities.definitions() if item.toggleable
        ]
        return sum(snapshot[item.capability_id] for item in toggleable), len(toggleable)
