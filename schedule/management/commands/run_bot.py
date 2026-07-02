import logging
from datetime import date, time as dtime, timedelta
from zoneinfo import ZoneInfo

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

logger = logging.getLogger(__name__)
UTC = ZoneInfo('UTC')
YUBORISH_VAQTI = dtime(13, 30, tzinfo=UTC)  # 18:30 Toshkent = 13:30 UTC

HAFTA_UZ = {
    'monday': 'DUSHANBA', 'tuesday': 'SESHANBA',
    'wednesday': 'CHORSHANBA', 'thursday': 'PAYSHANBA',
    'friday': 'JUMA', 'saturday': 'SHANBA', 'sunday': 'YAKSHANBA',
}
WEEKDAY = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

SECTIONS = [
    ('Frontend',         '📱'),
    ('IT',               '💻'),
    ("Sun'iy intellekt", '🤖'),
    ('Ingliz tili',      '🇬🇧'),
    ('SMM',              '📢'),
    ('Soft Skills',      '💡'),
]


def hafta_turi(d: date) -> str:
    return 'toq' if d.isocalendar()[1] % 2 == 1 else 'juft'


FAN_KOD = {
    'Frontend': 'FE',
    'IT': 'IT',
    "Sun'iy intellekt": 'AI',
}


def darslar_olish(target: date) -> dict:
    from schedule.models import Lesson
    qs = Lesson.objects.filter(
        ustoz__ism="Xurshid Yuldoshev",
        hafta_kuni=WEEKDAY[target.weekday()],
        hafta_turi__in=['har_doim', hafta_turi(target)],
        faol=True,
    ).select_related('ustoz').order_by('boshlanish_vaqti')
    grouped = {}
    for l in qs:
        grouped.setdefault(l.fan_nomi, []).append(l)
    return grouped


def mavzu_olish(lesson) -> str:
    from schedule.models import Dastur
    kod = FAN_KOD.get(lesson.fan_nomi)
    if kod and lesson.joriy_dars:
        dastur = Dastur.objects.filter(fan=kod, dars_raqami=lesson.joriy_dars).first()
        if dastur:
            return f"{lesson.joriy_dars}-dars: {dastur.sarlavha}"
    return lesson.mavzu or lesson.fan_nomi


def kun_matn(target: date, ogohlantirish='') -> str | None:
    grouped = darslar_olish(target)
    if not grouped:
        return None
    kun_nomi = HAFTA_UZ[WEEKDAY[target.weekday()]]
    qatorlar = [
        f"📅 <b>Ertangi dars jadvali</b>",
        f"<b>━━━━━━ {kun_nomi} ━━━━━━</b>",
        "",
    ]
    for fan_db, icon in SECTIONS:
        if fan_db not in grouped:
            continue
        qatorlar.append(f"{icon} <b>{fan_db}</b>")
        for l in grouped[fan_db]:
            vaqt = f"{l.boshlanish_vaqti.strftime('%H:%M')}–{l.tugash_vaqti.strftime('%H:%M')}"
            mavzu = mavzu_olish(l)
            qatorlar.append(f"  • <b>{l.guruh or '—'}</b>")
            qatorlar.append(f"    📖 {mavzu}")
            qatorlar.append(f"    ⏰ {vaqt}")
        qatorlar.append("")
    if ogohlantirish:
        qatorlar.append(ogohlantirish)
    return "\n".join(qatorlar)


def hafta_matn(dushanba: date, ogohlantirish='') -> str | None:
    qatorlar = ["📅 <b>Keyingi haftalik dars jadvali</b>", ""]
    topildi = False
    for i in range(6):
        d = dushanba + timedelta(days=i)
        grouped = darslar_olish(d)
        if not grouped:
            continue
        topildi = True
        kun = HAFTA_UZ[WEEKDAY[d.weekday()]]
        qatorlar.append(f"<b>━━━ {kun} ━━━</b>")
        for fan_db, icon in SECTIONS:
            if fan_db not in grouped:
                continue
            qatorlar.append(f"{icon} <b>{fan_db}</b>")
            for l in grouped[fan_db]:
                vaqt = f"{l.boshlanish_vaqti.strftime('%H:%M')}–{l.tugash_vaqti.strftime('%H:%M')}"
                mavzu = mavzu_olish(l)
                qatorlar.append(f"  • <b>{l.guruh or '—'}</b>: {mavzu}")
                qatorlar.append(f"    ⏰ {vaqt}")
        qatorlar.append("")
    if not topildi:
        return None
    if ogohlantirish:
        qatorlar.append(ogohlantirish)
    return "\n".join(qatorlar)


def qabul_tugma(xabar_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Qabul qildim", callback_data=f"qabul_{xabar_id}")
    ]])


class Command(BaseCommand):
    help = "Telegram botni ishga tushiradi — har kuni 18:30 da jadval yuboradi"

    def handle(self, *args, **options):
        from schedule.models import BotXabar

        app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

        async def on_qabul(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer("✅ Qabul qilindi!")
            xabar_id = int(query.data.split('_')[1])
            await sync_to_async(
                BotXabar.objects.filter(pk=xabar_id, qabul_qilindi=False).update
            )(qabul_qilindi=True, qabul_vaqti=timezone.now())
            try:
                await query.edit_message_reply_markup(reply_markup=None)
            except Exception:
                pass

        async def kunlik_yuborish(ctx: ContextTypes.DEFAULT_TYPE):
            ertaga = date.today() + timedelta(days=1)
            matn = await sync_to_async(kun_matn)(ertaga)
            if not matn:
                return
            xabar = await sync_to_async(BotXabar.objects.create)(
                chat_id=settings.TELEGRAM_CHAT_ID,
                jadval_sana=ertaga,
                haftalik=False,
            )
            msg = await ctx.bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=matn, parse_mode='HTML',
                reply_markup=qabul_tugma(xabar.pk),
            )
            await sync_to_async(BotXabar.objects.filter(pk=xabar.pk).update)(message_id=msg.message_id)

        async def haftalik_yuborish(ctx: ContextTypes.DEFAULT_TYPE):
            dushanba = date.today() + timedelta(days=1)
            matn = await sync_to_async(hafta_matn)(dushanba)
            if not matn:
                return
            xabar = await sync_to_async(BotXabar.objects.create)(
                chat_id=settings.TELEGRAM_CHAT_ID,
                jadval_sana=dushanba,
                haftalik=True,
            )
            msg = await ctx.bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=matn, parse_mode='HTML',
                reply_markup=qabul_tugma(xabar.pk),
            )
            await sync_to_async(BotXabar.objects.filter(pk=xabar.pk).update)(message_id=msg.message_id)

        async def qayta_yuborish(ctx: ContextTypes.DEFAULT_TYPE):
            bugundan = await sync_to_async(list)(
                BotXabar.objects.filter(qabul_qilindi=False, jadval_sana__gte=date.today())
            )
            ogohlantirish = "⚠️ <i>Hali qabul qilinmadi. Qayta yuborildi.</i>"
            for xabar in bugundan:
                target = xabar.jadval_sana
                if xabar.haftalik:
                    matn = await sync_to_async(hafta_matn)(target, ogohlantirish)
                else:
                    matn = await sync_to_async(kun_matn)(target, ogohlantirish)
                if not matn:
                    continue
                try:
                    msg = await ctx.bot.send_message(
                        chat_id=xabar.chat_id,
                        text=matn, parse_mode='HTML',
                        reply_markup=qabul_tugma(xabar.pk),
                    )
                    await sync_to_async(BotXabar.objects.filter(pk=xabar.pk).update)(
                        message_id=msg.message_id
                    )
                except Exception as e:
                    logger.error(f"Qayta yuborishda xato: {e}")

        app.add_handler(CallbackQueryHandler(on_qabul, pattern=r'^qabul_\d+$'))

        jq = app.job_queue
        jq.run_daily(kunlik_yuborish,  time=YUBORISH_VAQTI, days=(0, 1, 2, 3, 4, 5))
        jq.run_daily(haftalik_yuborish, time=YUBORISH_VAQTI, days=(6,))
        jq.run_repeating(qayta_yuborish, interval=300, first=300)

        self.stdout.write(self.style.SUCCESS(
            "Bot ishga tushdi. Har kuni 18:30 da xabar yuboriladi."
        ))
        app.run_polling()
