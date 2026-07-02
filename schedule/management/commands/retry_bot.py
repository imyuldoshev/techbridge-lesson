import asyncio
from datetime import date

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand

from telegram import Bot
from schedule.management.commands.run_bot import kun_matn, hafta_matn, qabul_tugma


class Command(BaseCommand):
    help = "Qabul qilinmagan xabarlarni hozir qayta yuboradi"

    def handle(self, *args, **options):
        asyncio.run(self._qayta())

    async def _qayta(self):
        from schedule.models import BotXabar

        qabul_qilinmaganlar = await sync_to_async(list)(
            BotXabar.objects.filter(qabul_qilindi=False, jadval_sana__gte=date.today())
        )

        if not qabul_qilinmaganlar:
            self.stdout.write(self.style.WARNING("Qabul qilinmagan xabar topilmadi."))
            return

        ogohlantirish = "⚠️ <i>Hali qabul qilinmadi. Qayta yuborildi.</i>"
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        async with bot:
            for xabar in qabul_qilinmaganlar:
                target = xabar.jadval_sana
                if xabar.haftalik:
                    matn = await sync_to_async(hafta_matn)(target, ogohlantirish)
                else:
                    matn = await sync_to_async(kun_matn)(target, ogohlantirish)
                if not matn:
                    continue
                msg = await bot.send_message(
                    chat_id=xabar.chat_id,
                    text=matn,
                    parse_mode='HTML',
                    reply_markup=qabul_tugma(xabar.pk),
                )
                await sync_to_async(BotXabar.objects.filter(pk=xabar.pk).update)(
                    message_id=msg.message_id
                )
                self.stdout.write(self.style.SUCCESS(f"Qayta yuborildi: {xabar.jadval_sana}"))
