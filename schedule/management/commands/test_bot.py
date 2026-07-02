import asyncio
from datetime import date, timedelta

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand

from telegram import Bot
from schedule.management.commands.run_bot import kun_matn, qabul_tugma


class Command(BaseCommand):
    help = "Ertangi jadval xabarini hozir test sifatida yuboradi"

    def handle(self, *args, **options):
        asyncio.run(self._yuborish())

    async def _yuborish(self):
        from schedule.models import BotXabar

        ertaga = date.today() + timedelta(days=1)
        matn = await sync_to_async(kun_matn)(ertaga)

        if not matn:
            self.stdout.write(self.style.WARNING("Ertaga dars topilmadi."))
            return

        xabar = await sync_to_async(BotXabar.objects.create)(
            chat_id=settings.TELEGRAM_CHAT_ID,
            jadval_sana=ertaga,
            haftalik=False,
        )

        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        async with bot:
            msg = await bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=matn,
                parse_mode='HTML',
                reply_markup=qabul_tugma(xabar.pk),
            )

        await sync_to_async(BotXabar.objects.filter(pk=xabar.pk).update)(message_id=msg.message_id)
        self.stdout.write(self.style.SUCCESS(f"Test xabari yuborildi! ({ertaga})"))
