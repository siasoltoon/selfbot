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


PANEL_CAPABILITIES: tuple[CapabilityDefinition, ...] = (
    # بازی میویی — قابلیت‌های اصلی
    CapabilityDefinition("panel_diamond_transfer", "💎 انتقال الماس", "انتقال الماس به آیدی/یوزرنیم یا کاربر ریپلای‌شده", category_id="myoi_core"),
    CapabilityDefinition("panel_personal_assistant", "🤖 دستیار شخصی", "دستیار فارسی برای اجرای فرمان‌های طبیعی روی سلف", category_id="myoi_core"),
    CapabilityDefinition("panel_self_management", "⚙️ مدیریت سلف", "روشن/خاموش کردن یکپارچه قابلیت‌های خودکار سلف", category_id="myoi_core"),
    CapabilityDefinition("panel_utility", "🧰 کاربردی", "وضعیت، امروز، آیدی و لغو عملیات", category_id="myoi_core"),
    CapabilityDefinition("panel_calculator", "🧮 محاسبات", "محاسبات مستقیم عبارات عددی و اعشاری", category_id="myoi_core"),
    CapabilityDefinition("panel_ping", "📡 پینگ", "نمایش زمان پاسخ سلف", category_id="myoi_core"),
    CapabilityDefinition("panel_information", "ℹ️ اطلاعات", "مدیریت و قطع نشست‌های فعال تلگرام", category_id="myoi_core"),
    CapabilityDefinition("panel_premium_clock", "🕐 ساعت پرمیوم", "به‌روزرسانی ایموجی وضعیت بر اساس ساعت فعلی", category_id="myoi_core"),
    CapabilityDefinition("panel_profile_photo", "🖼 عکس پروفایل", "تنظیم عکس پروفایل از پیام ریپلای‌شده", category_id="myoi_core"),
    CapabilityDefinition("panel_identity_clock", "🕰 ساعت", "ساعت/تاریخ در نام، فامیل و بیو و مدیریت فونت", category_id="myoi_core"),
    CapabilityDefinition("panel_online_mode", "🟢 حالت آنلاین", "مدیریت آنلاین ماندن دائمی حساب", category_id="myoi_core"),
    CapabilityDefinition("panel_action_mode", "🎭 حالت اکشن", "نمایش وضعیت تایپ، بازی، ویس و ویدیو در چت‌ها", category_id="myoi_core"),

    CapabilityDefinition("panel_diamond_transfer_direct", "انتقال با آیدی/یوزرنیم", "فرمت .انتقال [عدد] [آیدی/یوزرنیم]", category_id="myoi_core", parent_id="panel_diamond_transfer"),
    CapabilityDefinition("panel_diamond_transfer_reply", "انتقال با ریپلای", "انتقال الماس به کاربر پیام ریپلای‌شده", category_id="myoi_core", parent_id="panel_diamond_transfer"),
    CapabilityDefinition("panel_assistant_on", "هوش مصنوعی روشن", "فعال‌سازی فرمان طبیعی فارسی", category_id="myoi_core", parent_id="panel_personal_assistant"),
    CapabilityDefinition("panel_assistant_off", "هوش مصنوعی خاموش", "غیرفعال‌سازی دستیار شخصی", category_id="myoi_core", parent_id="panel_personal_assistant"),
    CapabilityDefinition("panel_assistant_name", "تغییر اسم هوش مصنوعی", "مشاهده یا تغییر trigger دستیار", category_id="myoi_core", parent_id="panel_personal_assistant"),
    CapabilityDefinition("panel_assistant_guide", "راهنمای دستیار شخصی", "راهنمای دوصفحه‌ای فرمان‌های طبیعی و پارامتری", category_id="myoi_core", parent_id="panel_personal_assistant"),
    CapabilityDefinition("panel_self_onoff", "روشن/خاموش سلف", "توقف یا ادامه قابلیت‌های خودکار", category_id="myoi_core", parent_id="panel_self_management"),
    CapabilityDefinition("panel_utility_status", "وضعیت", "نمایش وضعیت کلی", category_id="myoi_core", parent_id="panel_utility"),
    CapabilityDefinition("panel_utility_today", "امروز", "نمایش تاریخ و ساعت امروز", category_id="myoi_core", parent_id="panel_utility"),
    CapabilityDefinition("panel_utility_id", "آیدی", "نمایش اطلاعات آیدی خود یا هدف", category_id="myoi_core", parent_id="panel_utility"),
    CapabilityDefinition("panel_utility_cancel", "کنسل", "لغو عملیات در حال اجرا", category_id="myoi_core", parent_id="panel_utility"),
    CapabilityDefinition("panel_info_sessions", "نشست‌ها", "نمایش نشست‌های فعال حساب", category_id="myoi_core", parent_id="panel_information"),
    CapabilityDefinition("panel_info_disconnect", "قطع نشست", "قطع نشست با شماره فهرست", category_id="myoi_core", parent_id="panel_information"),
    CapabilityDefinition("panel_premium_clock_onoff", "روشن/خاموش ساعت پرمیوم", "فعال یا غیرفعال کردن ساعت پرمیوم", category_id="myoi_core", parent_id="panel_premium_clock"),
    CapabilityDefinition("panel_profile_set", "تنظیم پروفایل", "تغییر عکس پروفایل با ریپلای", category_id="myoi_core", parent_id="panel_profile_photo"),
    CapabilityDefinition("panel_identity_name", "ساعت/تاریخ نام", "افزودن یا حذف ساعت و تاریخ از نام", category_id="myoi_core", parent_id="panel_identity_clock"),
    CapabilityDefinition("panel_identity_family", "ساعت/تاریخ فامیل", "افزودن یا حذف ساعت و تاریخ از فامیل", category_id="myoi_core", parent_id="panel_identity_clock"),
    CapabilityDefinition("panel_identity_bio", "ساعت/تاریخ بیو", "مدیریت ساعت و متن‌های بیو", category_id="myoi_core", parent_id="panel_identity_clock"),
    CapabilityDefinition("panel_identity_fonts", "فونت ساعت", "انتخاب فونت ۱ تا ۲۰ یا رندوم", category_id="myoi_core", parent_id="panel_identity_clock"),
    CapabilityDefinition("panel_online_onoff", "آنلاین روشن/خاموش", "فعال یا غیرفعال کردن آنلاین ماندن", category_id="myoi_core", parent_id="panel_online_mode"),
    CapabilityDefinition("panel_action_chat", "حالت چت", "تایپ در پیوی/گروه", category_id="myoi_core", parent_id="panel_action_mode"),
    CapabilityDefinition("panel_action_game", "حالت بازی", "در حال بازی در پیوی/گروه", category_id="myoi_core", parent_id="panel_action_mode"),
    CapabilityDefinition("panel_action_voice", "حالت ویس", "در حال ضبط ویس در پیوی/گروه", category_id="myoi_core", parent_id="panel_action_mode"),
    CapabilityDefinition("panel_action_video", "حالت ویدیو مسیج", "در حال ضبط ویدیو مسیج در پیوی/گروه", category_id="myoi_core", parent_id="panel_action_mode"),

    # بازی میویی — خودکار
    CapabilityDefinition("panel_auto_cat", "🐈 پیشی خودکار", "تشخیص و اجرای خودکار برداشت میو پوینت", category_id="myoi_auto"),
    CapabilityDefinition("panel_auto_meow", "🐱 میو خودکار", "ارسال خودکار میو در بازه تنظیم‌شده", category_id="myoi_auto"),
    CapabilityDefinition("panel_auto_transfer", "💸 انتقال خودکار", "انتقال زمان‌بندی‌شده با مبلغ یا all", category_id="myoi_auto"),
    CapabilityDefinition("panel_auto_roulette", "🎰 رولت میویی", "اجرای خودکار رولت در گپ جاری", category_id="myoi_auto"),
    CapabilityDefinition("panel_auto_fishing", "🎣 ماهی‌گیری خودکار", "ماهی‌گیری و اکشن بر اساس سطح کمیابی", category_id="myoi_auto"),
    CapabilityDefinition("panel_auto_factory", "🏭 کارخونه میویی", "تولید و فروش زمان‌بندی‌شده محصولات", category_id="myoi_auto"),
    CapabilityDefinition("panel_auto_rescue", "🐈‍⬛ نجات خودکار", "نجات خودکار پیشی خیابونی در یک یا همه گپ‌ها", category_id="myoi_auto"),
    CapabilityDefinition("panel_auto_robbery", "🏦 سرقت میویی", "اجرای زمان‌بندی‌شده سرقت با نقش ثبت‌شده", category_id="myoi_auto"),
    CapabilityDefinition("panel_auto_cook", "🍳 آشپز میویی", "بررسی یخچال، پخت و فروش یا دادن ماهی", category_id="myoi_auto"),
    CapabilityDefinition("panel_auto_cat_schedule", "تنظیم زمان پیشی", "تنظیم فاصله اجرای پیشی", category_id="myoi_auto", parent_id="panel_auto_cat"),
    CapabilityDefinition("panel_auto_meow_schedule", "تنظیم زمان میو", "تنظیم فاصله ارسال میو", category_id="myoi_auto", parent_id="panel_auto_meow"),
    CapabilityDefinition("panel_auto_transfer_schedule", "زمان‌بندی انتقال", "زمان‌ها و مبلغ انتقال خودکار", category_id="myoi_auto", parent_id="panel_auto_transfer"),
    CapabilityDefinition("panel_auto_card_transfer", "کارت به کارت خودکار", "زمان‌بندی کارت به کارت به حساب ثابت", category_id="myoi_auto", parent_id="panel_auto_transfer"),
    CapabilityDefinition("panel_auto_deposit", "واریز خودکار", "زمان‌بندی واریز", category_id="myoi_auto", parent_id="panel_auto_transfer"),
    CapabilityDefinition("panel_auto_roulette_schedule", "زمان رولت", "فاصله اجرای رولت", category_id="myoi_auto", parent_id="panel_auto_roulette"),
    CapabilityDefinition("panel_auto_fishing_levels", "سطح‌های ماهی", "تنظیم اکشن پیشی/فروش/یخچال برای هر سطح", category_id="myoi_auto", parent_id="panel_auto_fishing"),
    CapabilityDefinition("panel_auto_factory_range", "محدوده فروش", "محدوده min-max قیمت بازار", category_id="myoi_auto", parent_id="panel_auto_factory"),
    CapabilityDefinition("panel_auto_factory_config", "تنظیم کارخانه", "محصول، درصد تولید و زمان تولید/فروش", category_id="myoi_auto", parent_id="panel_auto_factory"),
    CapabilityDefinition("panel_auto_factory_products", "محصولات", "فهرست محصولات و محدوده فروش", category_id="myoi_auto", parent_id="panel_auto_factory"),
    CapabilityDefinition("panel_auto_factory_status", "وضعیت کارخانه", "وضعیت و تنظیمات فعلی", category_id="myoi_auto", parent_id="panel_auto_factory"),
    CapabilityDefinition("panel_auto_rescue_all", "نجات همه گپ‌ها", "فعال یا غیرفعال کردن نجات سراسری", category_id="myoi_auto", parent_id="panel_auto_rescue"),
    CapabilityDefinition("panel_auto_rescue_notice", "اعلام نجات", "اعلام نجات موفق در Saved Messages", category_id="myoi_auto", parent_id="panel_auto_rescue"),
    CapabilityDefinition("panel_auto_robbery_config", "تنظیم سرقت", "نوع، جایگاه و فاصله اجرای سرقت", category_id="myoi_auto", parent_id="panel_auto_robbery"),
    CapabilityDefinition("panel_auto_cook_schedule", "تنظیم زمان آشپز", "فاصله بررسی یخچال", category_id="myoi_auto", parent_id="panel_auto_cook"),
    CapabilityDefinition("panel_auto_cook_result", "فروش/پیشی", "انتخاب فروش یا دادن ماهی پخته", category_id="myoi_auto", parent_id="panel_auto_cook"),

    # امنیت و کنترل
    CapabilityDefinition("panel_enemy", "🔥 دشمن", "مدیریت لیست دشمن و فحش", category_id="security"),
    CapabilityDefinition("panel_block", "🚫 بلاک", "بلاک و آنبلاک کاربران تلگرام", category_id="security"),
    CapabilityDefinition("panel_private_lock", "🔒 قفل پیوی", "قفل پیام خصوصی و لیست معاف‌ها", category_id="security"),
    CapabilityDefinition("panel_absence", "🌙 عدم حضور", "پیام عدم حضور بر اساس وضعیت یا حالت همیشه", category_id="security"),
    CapabilityDefinition("panel_secretary", "📨 منشی", "پاسخ خودکار پیوی بر اساس فاصله زمانی", category_id="security"),
    CapabilityDefinition("panel_forced_join", "⚙️ عضویت اجباری", "اجبار عضویت کاربران پیوی در کانال", category_id="security"),
    CapabilityDefinition("panel_mute", "🔇 سکوت", "نادیده گرفتن کاربران مشخص", category_id="security"),
    CapabilityDefinition("panel_word_filter", "🛡 فیلتر کلمات", "حذف پیام دارای کلمه فیلترشده در پیوی", category_id="security"),
    CapabilityDefinition("panel_enemy_users", "لیست دشمن", "افزودن/حذف/پاکسازی دشمن", category_id="security", parent_id="panel_enemy"),
    CapabilityDefinition("panel_enemy_profanity", "لیست فحش", "افزودن، حذف، دریافت و جایگزینی فایل فحش", category_id="security", parent_id="panel_enemy"),
    CapabilityDefinition("panel_block_manage", "مدیریت بلاک", "بلاک یا آنبلاک هدف", category_id="security", parent_id="panel_block"),
    CapabilityDefinition("panel_lock_exemptions", "معاف‌ها", "افزودن، حذف و فهرست معاف‌ها", category_id="security", parent_id="panel_private_lock"),
    CapabilityDefinition("panel_absence_message", "پیام عدم حضور", "ذخیره پیام عیناً از ریپلای", category_id="security", parent_id="panel_absence"),
    CapabilityDefinition("panel_absence_mode", "حالت عدم حضور", "آفلاین یا همیشه", category_id="security", parent_id="panel_absence"),
    CapabilityDefinition("panel_absence_threshold", "آستانه آفلاین", "تنظیم ۱ تا ۶۰ دقیقه", category_id="security", parent_id="panel_absence"),
    CapabilityDefinition("panel_absence_interval", "زمان عدم حضور", "فاصله ۱ تا ۷۲۰ ساعت", category_id="security", parent_id="panel_absence"),
    CapabilityDefinition("panel_secretary_message", "پیام منشی", "ذخیره پیام پاسخ خودکار", category_id="security", parent_id="panel_secretary"),
    CapabilityDefinition("panel_secretary_interval", "زمان منشی", "فاصله پاسخ با h یا d", category_id="security", parent_id="panel_secretary"),
    CapabilityDefinition("panel_secretary_status", "وضعیت منشی", "نمایش وضعیت، پیام و فاصله", category_id="security", parent_id="panel_secretary"),
    CapabilityDefinition("panel_forced_join_channel", "کانال عضویت", "تنظیم، حذف و نمایش کانال", category_id="security", parent_id="panel_forced_join"),
    CapabilityDefinition("panel_mute_manage", "مدیریت سکوت", "افزودن، حذف و فهرست سکوت", category_id="security", parent_id="panel_mute"),
    CapabilityDefinition("panel_filter_words", "کلمات فیلتر", "افزودن، حذف و پاکسازی کلمات", category_id="security", parent_id="panel_word_filter"),
    CapabilityDefinition("panel_filter_people", "افراد فیلتر", "اعمال/حذف/پاکسازی فیلتر کاربران", category_id="security", parent_id="panel_word_filter"),

    # محتوا و تعامل
    CapabilityDefinition("panel_content", "📦 محتوا", "ذخیره و جایگزینی محتوای نام‌گذاری‌شده", category_id="content"),
    CapabilityDefinition("panel_auto_reply", "💬 پاسخ خودکار", "پاسخ خودکار پیوی بر اساس کلمه کلیدی", category_id="content"),
    CapabilityDefinition("panel_tag_members", "👥 تگ اعضا", "تگ گروهی اعضای گروه", category_id="content"),
    CapabilityDefinition("panel_group_management", "👮 مدیریت گروه", "پین، حذف پین، بن و بن سراسری", category_id="content"),
    CapabilityDefinition("panel_chat_guard", "🛡 نگهبان چت", "ذخیره پیام با حالت‌های تایم‌دار، ویرایش، حذف و مدیا", category_id="content"),
    CapabilityDefinition("panel_auto_read", "👁 سین خودکار", "سین خودکار پیوی، گروه، کانال و ربات", category_id="content"),
    CapabilityDefinition("panel_auto_reaction", "❤️ ری‌اکشن خودکار", "واکنش خودکار به پیام‌های کاربران", category_id="content"),
    CapabilityDefinition("panel_first_comment", "💬 کامنت اول خودکار", "ثبت و ارسال کامنت اول برای کانال‌ها", category_id="content"),
    CapabilityDefinition("panel_spam", "🥷 اسپم", "ارسال تکراری با سقف ۳۰۰", category_id="content"),
    CapabilityDefinition("panel_sender", "📣 سندر", "ارسال بنر کپی/فور با سهمیه و تأخیر", category_id="content"),
    CapabilityDefinition("panel_tabchi", "📢 تبچی", "ارسال زمان‌بندی‌شده بنرها به اهداف", category_id="content"),
    CapabilityDefinition("panel_content_manage", "مدیریت محتوا", "روشن/خاموش، ایجاد، ذخیره، حذف و فهرست", category_id="content", parent_id="panel_content"),
    CapabilityDefinition("panel_auto_reply_manage", "مدیریت پاسخ‌ها", "روشن/خاموش، ایجاد، ذخیره، حذف و فهرست", category_id="content", parent_id="panel_auto_reply"),
    CapabilityDefinition("panel_group_ban", "بن گروه", "بن، آن‌بن و فهرست بن سراسری", category_id="content", parent_id="panel_group_management"),
    CapabilityDefinition("panel_group_pin", "پین", "پین و حذف پین با ریپلای", category_id="content", parent_id="panel_group_management"),
    CapabilityDefinition("panel_guard_timed", "ذخیره تایم‌دار", "ذخیره پیام بر اساس زمان", category_id="content", parent_id="panel_chat_guard"),
    CapabilityDefinition("panel_guard_edit", "ذخیره ویرایش", "ذخیره تغییرات پیام", category_id="content", parent_id="panel_chat_guard"),
    CapabilityDefinition("panel_guard_delete", "ذخیره حذف", "ذخیره پیام‌های حذف‌شده", category_id="content", parent_id="panel_chat_guard"),
    CapabilityDefinition("panel_guard_media", "ذخیره مدیا", "ذخیره رسانه‌های چت", category_id="content", parent_id="panel_chat_guard"),
    CapabilityDefinition("panel_auto_read_modes", "حالت‌های سین", "پیوی، گروه، کانال و ربات", category_id="content", parent_id="panel_auto_read"),
    CapabilityDefinition("panel_reaction_manage", "مدیریت ری‌اکشن", "ثبت، حذف، فهرست و پاکسازی", category_id="content", parent_id="panel_auto_reaction"),
    CapabilityDefinition("panel_first_comment_channels", "کانال‌های کامنت", "ثبت/حذف/فهرست/پاکسازی کانال‌ها", category_id="content", parent_id="panel_first_comment"),
    CapabilityDefinition("panel_spam_text", "اسپم متن", "اسپم متن یا پیام ریپلای‌شده", category_id="content", parent_id="panel_spam"),
    CapabilityDefinition("panel_sender_banner", "بنر سندر", "بنر کپی یا فور", category_id="content", parent_id="panel_sender"),
    CapabilityDefinition("panel_sender_quota", "سهمیه سندر", "۵۰ تا ۲۰۰ ارسال در ساعت", category_id="content", parent_id="panel_sender"),
    CapabilityDefinition("panel_sender_delay", "تاخیر سندر", "فاصله ارسال بر حسب ثانیه", category_id="content", parent_id="panel_sender"),
    CapabilityDefinition("panel_tabchi_banners", "بنرهای تبچی", "ثبت، حذف، فهرست و پاکسازی", category_id="content", parent_id="panel_tabchi"),
    CapabilityDefinition("panel_tabchi_targets", "اهداف تبچی", "گپ هدف و همه گپ‌ها", category_id="content", parent_id="panel_tabchi"),
    CapabilityDefinition("panel_tabchi_recent_pv", "پیوی‌های اخیر", "فوروارد به تعداد پیوی اخیر", category_id="content", parent_id="panel_tabchi"),

    # ابزارها
    CapabilityDefinition("panel_translate", "🌐 ترجمه", "ترجمه ریپلای یا متن مستقیم با کد زبان", category_id="tools"),
    CapabilityDefinition("panel_downloader", "⬇️ دانلودر", "دانلود یوتیوب و اینستاگرام", category_id="tools"),
    CapabilityDefinition("panel_currency", "💱 قیمت ارز", "استعلام قیمت ارز", category_id="tools"),
    CapabilityDefinition("panel_delete", "🗑 حذف پیام", "حذف پیام ریپلای یا تعداد مشخص پیام خود", category_id="tools"),
    CapabilityDefinition("panel_games", "🎲 بازی و کازینو", "تاس، دارت، بولینگ، بسکتبال و کازینو", category_id="tools"),
    CapabilityDefinition("panel_voice_search", "🎙 سرچ ویس آماده", "جست‌وجو و فوروارد ویس ذخیره‌شده", category_id="tools"),
    CapabilityDefinition("panel_tts", "🔊 متن به ویس", "TTS، STT و انتخاب صدای پیش‌فرض", category_id="tools"),
    CapabilityDefinition("panel_premium_emoji", "✨ ایموجی پریمیوم", "جایگزینی ایموجی معمولی با ایموجی پریمیوم ثبت‌شده", category_id="tools"),
    CapabilityDefinition("panel_stars_challenge", "⭐ استارزی", "تنظیم و باز کردن خودکار محتوای استارزی", category_id="tools"),
    CapabilityDefinition("panel_image_quality", "🖼 کیفیت عکس", "بهبود کیفیت عکس ریپلای‌شده", category_id="tools"),
    CapabilityDefinition("panel_translate_reply", "ترجمه ریپلای", "ترجمه پیام ریپلای‌شده", category_id="tools", parent_id="panel_translate"),
    CapabilityDefinition("panel_translate_direct", "ترجمه مستقیم", "ترجمه متن با کد زبان", category_id="tools", parent_id="panel_translate"),
    CapabilityDefinition("panel_downloader_youtube", "یوتیوب", "دانلود و ارسال کیفیت موجود", category_id="tools", parent_id="panel_downloader"),
    CapabilityDefinition("panel_downloader_instagram", "اینستاگرام", "دانلود پست، ریلز و استوری", category_id="tools", parent_id="panel_downloader"),
    CapabilityDefinition("panel_delete_one", "حذف ریپلای", "حذف پیام ریپلای و دستور", category_id="tools", parent_id="panel_delete"),
    CapabilityDefinition("panel_delete_many", "حذف چند پیام", "حذف تعداد مشخص پیام اخیر خود", category_id="tools", parent_id="panel_delete"),
    CapabilityDefinition("panel_games_dice", "تاس/دارت/بولینگ/بسکتبال", "ارسال دایس تلگرام", category_id="tools", parent_id="panel_games"),
    CapabilityDefinition("panel_games_casino", "کازینو", "بازی اسلات تلگرام", category_id="tools", parent_id="panel_games"),
    CapabilityDefinition("panel_voice_search_manage", "ویس‌های آماده", "فهرست و جست‌وجوی جزئی/دقیق", category_id="tools", parent_id="panel_voice_search"),
    CapabilityDefinition("panel_tts_speak", "متن به ویس", "صدای مرد/زن یا صدای پیش‌فرض", category_id="tools", parent_id="panel_tts"),
    CapabilityDefinition("panel_tts_transcribe", "ویس به متن", "تبدیل ویس ریپلای به متن", category_id="tools", parent_id="panel_tts"),
    CapabilityDefinition("panel_tts_default_voice", "صدای پیش‌فرض", "تنظیم صدای مرد یا زن", category_id="tools", parent_id="panel_tts"),
    CapabilityDefinition("panel_emoji_toggle", "ایموجی پریمیوم روشن/خاموش", "فعال یا غیرفعال کردن جایگزینی", category_id="tools", parent_id="panel_premium_emoji"),
    CapabilityDefinition("panel_emoji_list", "لیست ایموجی‌ها", "نمایش ایموجی‌های ثبت‌شده", category_id="tools", parent_id="panel_premium_emoji"),
    CapabilityDefinition("panel_emoji_cleanup", "پاکسازی ایموجی‌ها", "حذف همه ثبت‌ها", category_id="tools", parent_id="panel_premium_emoji"),
    CapabilityDefinition("panel_stars_media", "محتوای استارزی", "تنظیم عکس/پیام استارزی", category_id="tools", parent_id="panel_stars_challenge"),
    CapabilityDefinition("panel_stars_time", "زمان استارزی", "تنظیم HH:MM", category_id="tools", parent_id="panel_stars_challenge"),
    CapabilityDefinition("panel_stars_toggle", "روشن/خاموش استارزی", "فعال یا غیرفعال کردن بازکردن خودکار", category_id="tools", parent_id="panel_stars_challenge"),
    CapabilityDefinition("panel_image_quality_reply", "بهبود عکس", "افزایش کیفیت عکس ریپلای‌شده", category_id="tools", parent_id="panel_image_quality"),
)

INTERNAL_CAPABILITIES: tuple[CapabilityDefinition, ...] = (
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


CAPABILITIES: tuple[CapabilityDefinition, ...] = INTERNAL_CAPABILITIES + PANEL_CAPABILITIES

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
        if enabled and definition.parent_id:
            parent = self.definition(definition.parent_id)
            enabled_state[parent.capability_id] = True
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
