import asyncio
from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from telegram import Bot

from schedule.management.commands.run_bot import hafta_matn, qabul_tugma
from schedule.models import BotXabar


class Command(BaseCommand):
    help = "Haftalik test xabarini Telegram ga yuboradi"

    def handle(self, *args, **options):
        dushanba = date.today()
        while dushanba.weekday() != 0:
            dushanba += timedelta(days=1)

        matn = hafta_matn(dushanba)
        if not matn:
            self.stdout.write(self.style.WARNING("Jadval topilmadi."))
            return

        xabar = BotXabar.objects.create(
            chat_id=settings.TELEGRAM_CHAT_ID,
            jadval_sana=dushanba,
            haftalik=True,
        )

        async def yuborish():
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            msg = await bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=matn,
                parse_mode='HTML',
                reply_markup=qabul_tugma(xabar.pk),
            )
            BotXabar.objects.filter(pk=xabar.pk).update(message_id=msg.message_id)

        asyncio.run(yuborish())
        self.stdout.write(self.style.SUCCESS(f"Haftalik test xabari yuborildi! ({dushanba})"))
