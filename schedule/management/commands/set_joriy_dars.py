from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "FE guruhlari joriy dars raqamlarini belgilaydi"

    def handle(self, *args, **options):
        from schedule.models import Lesson

        # FE guruhlari uchun joriy dars raqamlari
        # Bu qiymatlarni kerak bo'lganda o'zgartirishingiz mumkin
        fe_joriy = {
            'FE-1': 37,
            'FE-2': 27,
            'FE-3': 16,
        }

        jami = 0
        for guruh, dars_raqami in fe_joriy.items():
            count = Lesson.objects.filter(
                fan_nomi='Frontend',
                guruh=guruh,
            ).update(joriy_dars=dars_raqami)
            self.stdout.write(f"  {guruh}: joriy_dars={dars_raqami} ({count} ta dars yangilandi)")
            jami += count

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor! Jami {jami} ta Frontend darsi yangilandi."
        ))
        self.stdout.write(
            "IT va AI guruhlari uchun joriy dars raqamini admin paneldan kiriting:\n"
            "  Darslar → Lesson ro'yxatida 'Joriy dars raqami' ustunini to'g'ridan to'g'ri o'zgartiring."
        )
