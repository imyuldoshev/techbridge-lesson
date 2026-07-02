from django.core.management.base import BaseCommand

from schedule.models import Lesson, Teacher

# Yakkabog' guruhlari → (boshlanish, tugash, dars_raqami)
GROUPS = {
    'INFINITY': ('08:00', '10:00', 1),
    'AURORA':   ('10:00', '12:00', 2),
    'NEXUS':    ('10:00', '12:00', 2),
    'ZENITH':   ('14:00', '16:00', 3),
    'NOVA':     ('14:00', '16:00', 3),
    'TITANIUM': ('16:00', '18:00', 4),
}

# FE guruhlari → (boshlanish, tugash, dars_raqami)
FE_GROUPS = {
    'FE-1': ('08:00', '10:00', 1),
    'FE-2': ('10:00', '12:00', 2),
    'FE-3': ('16:00', '18:00', 4),
}

# FE darslar haftaning toq kunlarida (dushanba, chorshanba, juma)
FE_DAYS = ['monday', 'wednesday', 'friday']

# IT_SS  = toq hafta IT,  juft hafta Soft Skills  (AURORA, ZENITH, TITANIUM shanba)
# SS_AI  = toq hafta SS, juft hafta AI            (NEXUS, NOVA shanba — IT guruhlar IT o'tganda bular SS, aksincha AI)
SCHEDULE = {
    'INFINITY': {
        'monday': 'IT',    'tuesday': 'AI',  'wednesday': 'ENG',
        'thursday': 'IT_SS', 'friday': 'ENG',  'saturday': 'SMM',
    },
    'AURORA': {
        'monday': 'IT',    'tuesday': 'ENG', 'wednesday': 'SMM',
        'thursday': 'AI',  'friday': 'ENG',  'saturday': 'IT_SS',
    },
    'NEXUS': {
        'monday': 'ENG',   'tuesday': 'IT',  'wednesday': 'ENG',
        'thursday': 'SMM', 'friday': 'IT',   'saturday': 'SS_AI',
    },
    'ZENITH': {
        'monday': 'IT',    'tuesday': 'ENG', 'wednesday': 'SMM',
        'thursday': 'AI',  'friday': 'ENG',  'saturday': 'IT_SS',
    },
    'NOVA': {
        'monday': 'ENG',   'tuesday': 'IT',  'wednesday': 'ENG',
        'thursday': 'SMM', 'friday': 'IT',   'saturday': 'SS_AI',
    },
    'TITANIUM': {
        'monday': 'SMM',   'tuesday': 'AI',  'wednesday': 'ENG',
        'thursday': 'ENG', 'friday': 'IT',   'saturday': 'IT_SS',
    },
}

FAN_NOMI = {
    'IT':  'IT',
    'AI':  "Sun'iy intellekt",
    'ENG': 'Ingliz tili',
    'SMM': 'SMM',
    'SS':  'Soft Skills',
}


class Command(BaseCommand):
    help = "Eski ma'lumotlarni o'chirib Yakkabog' jadvalini yuklaydi"

    def handle(self, *args, **options):
        self.stdout.write("Eski ma'lumotlar o'chirilmoqda...")
        Lesson.objects.all().delete()
        Teacher.objects.all().delete()

        self.stdout.write('Ustozlar yaratilmoqda...')
        xurshid    = Teacher.objects.create(ism="Xurshid Yuldoshev",  mutaxassislik="Frontend / IT / Sun'iy intellekt")
        dilshodbek = Teacher.objects.create(ism="Dilshodbek Bozorov", mutaxassislik="IT")
        abror      = Teacher.objects.create(ism="Abror Norqobilov",   mutaxassislik="Ingliz tili")
        asomiddin  = Teacher.objects.create(ism="Asomiddin Jumayev",  mutaxassislik="SMM")
        elyor      = Teacher.objects.create(ism="Elyor Mamasoatov",   mutaxassislik="Soft Skills")

        def get_teacher(group, day, subject):
            if subject == 'IT':
                if day in ('monday', 'friday'):
                    return dilshodbek
                return xurshid
            elif subject == 'AI':
                return xurshid
            elif subject == 'ENG':
                return abror
            elif subject == 'SMM':
                return asomiddin
            elif subject == 'SS':
                return elyor

        def make_lesson(group, day, subject, hafta_turi, vaqt_bosh, vaqt_tug, dars):
            teacher = get_teacher(group, day, subject)
            Lesson.objects.create(
                ustoz=teacher,
                hafta_kuni=day,
                hafta_turi=hafta_turi,
                boshlanish_vaqti=vaqt_bosh,
                tugash_vaqti=vaqt_tug,
                dars_raqami=dars,
                fan_nomi=FAN_NOMI[subject],
                mavzu=FAN_NOMI[subject],
                guruh=group,
                faol=True,
            )

        self.stdout.write('Darslar yaratilmoqda...')
        count = 0
        for group, days in SCHEDULE.items():
            vaqt_bosh, vaqt_tug, dars = GROUPS[group]
            for day, subj_code in days.items():
                if subj_code == 'IT_SS':
                    make_lesson(group, day, 'IT', 'toq',  vaqt_bosh, vaqt_tug, dars)
                    make_lesson(group, day, 'SS', 'juft', vaqt_bosh, vaqt_tug, dars)
                    count += 2
                elif subj_code == 'SS_AI':
                    make_lesson(group, day, 'SS', 'toq',  vaqt_bosh, vaqt_tug, dars)
                    make_lesson(group, day, 'AI', 'juft', vaqt_bosh, vaqt_tug, dars)
                    count += 2
                else:
                    make_lesson(group, day, subj_code, 'har_doim', vaqt_bosh, vaqt_tug, dars)
                    count += 1

        self.stdout.write('FE guruhlari yaratilmoqda...')
        for group, (vaqt_bosh, vaqt_tug, dars) in FE_GROUPS.items():
            for day in FE_DAYS:
                Lesson.objects.create(
                    ustoz=xurshid,
                    hafta_kuni=day,
                    hafta_turi='har_doim',
                    boshlanish_vaqti=vaqt_bosh,
                    tugash_vaqti=vaqt_tug,
                    dars_raqami=dars,
                    fan_nomi='Frontend',
                    mavzu='5-modul: Tailwind CSS (yakunlandi) → 6-modul: JavaScript',
                    guruh=group,
                    faol=True,
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor! 7 ustoz va {count} ta dars muvaffaqiyatli yaratildi."
        ))
