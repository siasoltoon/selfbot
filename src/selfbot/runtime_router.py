"""Runtime routing from Telegram events to safe built-in commands."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import ast
import operator
from typing import Protocol
from .errors import AuthorizationError, NotFoundError, ValidationError
from .services import CoreServices


class TelegramTransport(Protocol):
    events: object
    async def send_message(self, chat_id: str | int, text: str, *, account_id: str | None = None): ...
    async def open_panel(self, chat_id: str | int, *, owner_id: str, account_id: str | None = None): ...
    async def resolve_user_id(self, identifier: str, *, account_id: str | None = None) -> str: ...


@dataclass(slots=True)
class TelegramRuntimeRouter:
    telegram: TelegramTransport
    owner_id: str | None
    allow_linked_accounts: bool = False
    services: CoreServices | None = None

    def start(self) -> None:
        self.telegram.events.subscribe("telegram.new_message", self._handle_message)

    async def _send(self, event, text: str) -> None:
        account_id = event.payload.get("telegram_account_id")
        await self.telegram.send_message(
            event.chat_id or event.actor_id,
            text,
            account_id=account_id,
        )

    @staticmethod
    def _command(text: str) -> tuple[str, list[str]]:
        parts = text.split()
        if not parts:
            return "", []
        return parts[0].split("@", 1)[0].lower(), parts[1:]


    @staticmethod
    def _safe_calculate(expression: str) -> int | float:
        if len(expression) > 200:
            raise ValidationError("عبارت بیش از حد طولانی است")
        allowed = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.USub: operator.neg, ast.UAdd: operator.pos}
        tree = ast.parse(expression.replace("×", "*").replace("÷", "/"), mode="eval")
        def visit(node):
            if isinstance(node, ast.Expression): return visit(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool): return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in allowed:
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Div) and right == 0: raise ValidationError("تقسیم بر صفر مجاز نیست")
                result = allowed[type(node.op)](left, right)
                if abs(result) > 10**15: raise ValidationError("نتیجه بیش از حد بزرگ است")
                return result
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed: return allowed[type(node.op)](visit(node.operand))
            raise ValidationError("عبارت محاسباتی نامعتبر است")
        return visit(tree)

    async def _require_capability(self, event, owner_id: str, capability_id: str) -> bool:
        if self.services is None:
            return True
        try:
            self.services.capabilities.require(owner_id, capability_id)
            return True
        except (ValidationError, NotFoundError) as exc:
            await self._send(event, f"این قابلیت خاموش است: {exc}")
            return False

    async def _handle_message(self, event) -> None:
        if self.owner_id:
            if event.actor_id != self.owner_id:
                return
        elif not self.allow_linked_accounts:
            return

        # Commands are deliberately restricted to messages sent by the connected
        # account itself. This prevents a group member from controlling the owner.
        if "outgoing" in event.payload and not bool(event.payload.get("outgoing")):
            return

        text = str(event.payload.get("text") or "").strip()
        if not (text.startswith("/") or text.startswith(".")):
            return

        command, args = self._command(text)
        account_id = event.payload.get("telegram_account_id")
        owner_id = str(event.actor_id or self.owner_id or "").strip()

        if command in {"/panel", "/پنل"}:
            try:
                await self.telegram.open_panel(
                    event.chat_id or owner_id,
                    owner_id=owner_id,
                    account_id=account_id,
                )
            except Exception:
                await self._send(
                    event,
                    "پنل تعاملی در دسترس نیست. قابلیت Inline Mode ربات مدیریت را بررسی کن.",
                )
            return

        if command in {".موجودی", "/موجودی"}:
            if self.services is None:
                await self._send(event, "سرویس اقتصاد در دسترس نیست.")
                return
            try:
                self.services.economy.capabilities.require(owner_id, self.services.economy.DOMAIN_CAPABILITY)
                balance = self.services.economy.balance(owner_id)
                await self._send(event, f"💎 موجودی شما: {balance:,} الماس")
            except (ValidationError, NotFoundError) as exc:
                await self._send(event, f"موجودی قابل دریافت نیست: {exc}")
            return

        if command in {".تاریخچه", ".تاریخچه_تراکنش", "/تاریخچه"}:
            if self.services is None:
                await self._send(event, "سرویس اقتصاد در دسترس نیست.")
                return
            try:
                self.services.economy.capabilities.require(owner_id, self.services.economy.DOMAIN_CAPABILITY)
                rows = self.services.economy.history(owner_id, limit=10)
                if not rows:
                    await self._send(event, "💎 هنوز تراکنشی ثبت نشده است.")
                    return
                lines = ["💎 آخرین تراکنش‌ها:"]
                for row in rows:
                    if row.kind == "transfer":
                        direction = "ارسال" if row.sender_id == owner_id else "دریافت"
                        lines.append(f"• {direction}: {row.amount:,} | کارمزد: {row.fee:,}")
                    else:
                        direction = "افزایش ادمین" if row.kind == "admin_credit" else "کاهش ادمین"
                        lines.append(f"• {direction}: {row.amount:,}")
                await self._send(event, "\n".join(lines))
            except (ValidationError, NotFoundError) as exc:
                await self._send(event, f"تاریخچه قابل دریافت نیست: {exc}")
            return

        if command in {".انتقال", "/انتقال"}:
            if self.services is None or not args:
                await self._send(event, "فرمت: .انتقال [مقدار] [@username/ID] یا Reply")
                return
            try:
                amount = int(args[0])
            except ValueError:
                await self._send(event, "مقدار الماس باید عدد صحیح باشد.")
                return
            target = args[1] if len(args) >= 2 else event.payload.get("reply_to_user_id")
            if not target:
                await self._send(event, "مقصد را با @username/ID یا Reply مشخص کن.")
                return
            try:
                if str(target).startswith("@") and hasattr(self.telegram, "resolve_user_id"):
                    target = await self.telegram.resolve_user_id(str(target), account_id=account_id)
                recipient = str(target).strip()
                result = self.services.economy.transfer(owner_id, recipient, amount)
                await self._send(
                    event,
                    f"✅ انتقال انجام شد.\n💎 مبلغ: {result.amount:,}\n💳 کارمزد: {result.fee:,}\n💎 موجودی جدید: {result.sender_balance:,}",
                )
            except (ValidationError, NotFoundError, AuthorizationError) as exc:
                await self._send(event, f"❌ انتقال انجام نشد: {exc}")
            return

        if command in {".افزایش", "/افزایش"} and len(args) >= 3 and args[0] == "الماس":
            if self.services is None:
                await self._send(event, "سرویس اقتصاد در دسترس نیست.")
                return
            try:
                amount = int(args[1])
                target = args[2]
                if str(target).startswith("@") and hasattr(self.telegram, "resolve_user_id"):
                    target = await self.telegram.resolve_user_id(str(target), account_id=account_id)
                balance = self.services.economy.adjust(owner_id, str(target), amount, reason=" ".join(args[3:]) or "admin credit")
                await self._send(event, f"✅ {amount:,} الماس اضافه شد. موجودی جدید: {balance:,}")
            except (ValueError, ValidationError, AuthorizationError, NotFoundError) as exc:
                await self._send(event, f"❌ افزایش الماس انجام نشد: {exc}")
            return

        if command in {".کاهش", "/کاهش"} and len(args) >= 3 and args[0] == "الماس":
            if self.services is None:
                await self._send(event, "سرویس اقتصاد در دسترس نیست.")
                return
            try:
                amount = int(args[1])
                if amount <= 0:
                    raise ValidationError("مقدار باید مثبت باشد")
                target = args[2]
                if str(target).startswith("@") and hasattr(self.telegram, "resolve_user_id"):
                    target = await self.telegram.resolve_user_id(str(target), account_id=account_id)
                balance = self.services.economy.adjust(owner_id, str(target), -amount, reason=" ".join(args[3:]) or "admin debit")
                await self._send(event, f"✅ {amount:,} الماس کم شد. موجودی جدید: {balance:,}")
            except (ValueError, ValidationError, AuthorizationError, NotFoundError) as exc:
                await self._send(event, f"❌ کاهش الماس انجام نشد: {exc}")
            return


        if command in {".پینگ", "/پینگ", "/ping"}:
            if await self._require_capability(event, owner_id, "panel_ping"):
                await self._send(event, "🏓 pong")
            return
        if command in {".وضعیت", "/وضعیت"}:
            if await self._require_capability(event, owner_id, "panel_utility_status"):
                snapshot = self.services.capabilities.snapshot(owner_id)
                await self._send(event, f"🟢 Selfbot فعال است. قابلیت‌های روشن: {sum(snapshot.values())}/{len(snapshot)}")
            return
        if command in {".امروز", "/امروز"}:
            if await self._require_capability(event, owner_id, "panel_utility_today"):
                now = datetime.now().astimezone()
                await self._send(event, f"📅 {now.strftime('%Y-%m-%d')}\\n🕐 {now.strftime('%H:%M:%S %Z')}")
            return
        if command in {".ایدی", "/ایدی"}:
            if await self._require_capability(event, owner_id, "panel_utility_id"):
                await self._send(event, f"🆔 آیدی عددی: {event.payload.get('reply_to_user_id') or owner_id}")
            return
        if command in {".کنسل", "/کنسل"}:
            if await self._require_capability(event, owner_id, "panel_utility_cancel"):
                cancelled = self.services.tasks.cancel_for_owner(owner_id)
                await self._send(event, f"🛑 {cancelled} عملیات لغو شد.")
            return
        if text.startswith(".") and command not in {".موجودی", ".تاریخچه", ".تاریخچه_تراکنش", ".انتقال", ".افزایش", ".کاهش"}:
            expression = text[1:].strip()
            if expression and any(ch.isdigit() for ch in expression) and any(ch in expression for ch in "+-*/×÷"):
                if await self._require_capability(event, owner_id, "panel_calculator"):
                    try:
                        result = self._safe_calculate(expression)
                        await self._send(event, f"🧮 {result:g}" if isinstance(result, float) else f"🧮 {result}")
                    except (ValueError, SyntaxError, ValidationError) as exc:
                        await self._send(event, f"❌ محاسبه نامعتبر است: {exc}")
                return

        if command == "/ping":
            await self._send(event, "pong")
            return

        if command == "/status":
            if self.services is None:
                await self._send(event, "Selfbot is running.")
                return
            snapshot = self.services.capabilities.snapshot(owner_id)
            enabled = sum(snapshot.values())
            await self._send(event, f"Selfbot فعال است. قابلیت‌های روشن: {enabled}/{len(snapshot)}")
            return

        if command in {"/capability", "/قابلیت"}:
            if self.services is None:
                await self._send(event, "Capability service is unavailable.")
                return
            if len(args) != 2 or args[1].lower() not in {"on", "off", "روشن", "خاموش"}:
                await self._send(event, "فرمت: /capability <id> on|off")
                return
            capability_id = args[0].strip().lower()
            enabled = args[1].lower() in {"on", "روشن"}
            try:
                self.services.capabilities.set_enabled(owner_id, capability_id, enabled)
            except (ValidationError, NotFoundError) as exc:
                await self._send(event, f"تغییر قابلیت انجام نشد: {exc}")
                return
            state = "روشن" if enabled else "خاموش"
            await self._send(event, f"قابلیت «{capability_id}» {state} شد.")
            return

        if command == "/help":
            await self._send(
                event,
                "دستورات فعال:\n/panel یا /پنل\n/status\n/capability <id> on|off\n/help",
            )
