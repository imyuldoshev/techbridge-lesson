from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher_profile')
    ism = models.CharField(max_length=200)
    telegram_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    telefon = models.CharField(max_length=20, blank=True, null=True)
    mutaxassislik = models.CharField(max_length=100, blank=True, null=True)
    yaratilgan_sana = models.DateTimeField(auto_now_add=True)
    yangilangan_sana = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ism']

    def __str__(self):
        return self.ism


class Lesson(models.Model):
    HAFTA_KUNI_CHOICES = [
        ('monday', 'Dushanba'),
        ('tuesday', 'Seshanba'),
        ('wednesday', 'Chorshanba'),
        ('thursday', 'Payshanba'),
        ('friday', 'Juma'),
        ('saturday', 'Shanba'),
        ('sunday', 'Yakshanba'),
    ]

    HAFTA_TURI_CHOICES = [
        ('har_doim', 'Har doim'),
        ('toq', 'Toq hafta (1, 3, 5...)'),
        ('juft', 'Juft hafta (2, 4, 6...)'),
    ]

    ustoz = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='darslar')
    hafta_kuni = models.CharField(max_length=10, choices=HAFTA_KUNI_CHOICES)
    hafta_turi = models.CharField(max_length=10, choices=HAFTA_TURI_CHOICES, default='har_doim')
    boshlanish_vaqti = models.TimeField()
    tugash_vaqti = models.TimeField()
    dars_raqami = models.IntegerField()
    fan_nomi = models.CharField(max_length=100)
    mavzu = models.TextField()
    xona = models.CharField(max_length=20, blank=True, null=True)
    guruh = models.CharField(max_length=50, blank=True, null=True)
    faol = models.BooleanField(default=True)
    eslatma = models.TextField(blank=True, null=True)
    yaratilgan_sana = models.DateTimeField(auto_now_add=True)
    yangilangan_sana = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hafta_kuni', 'boshlanish_vaqti']
        unique_together = ['ustoz', 'hafta_kuni', 'dars_raqami', 'hafta_turi', 'guruh']

    def __str__(self):
        return f"{self.fan_nomi} - {self.ustoz.ism} ({self.get_hafta_kuni_display()})"

    def clean(self):
        if self.dars_raqami is not None and not (1 <= self.dars_raqami <= 8):
            raise ValidationError({'dars_raqami': "Dars raqami 1 dan 8 gacha bo'lishi kerak."})
        if self.boshlanish_vaqti and self.tugash_vaqti and self.boshlanish_vaqti >= self.tugash_vaqti:
            raise ValidationError({'tugash_vaqti': "Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak."})

        if self.ustoz_id and self.hafta_kuni and self.dars_raqami is not None and self.guruh:
            qs = Lesson.objects.filter(
                ustoz_id=self.ustoz_id, hafta_kuni=self.hafta_kuni,
                dars_raqami=self.dars_raqami, guruh=self.guruh,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if self.hafta_turi == 'har_doim':
                conflict = qs.exists()
            else:
                conflict = qs.filter(hafta_turi__in=['har_doim', self.hafta_turi]).exists()
            if conflict:
                raise ValidationError(
                    "Bu guruhning shu kunda, shu dars raqamida va shu hafta turida boshqa darsi mavjud."
                )


class BotXabar(models.Model):
    message_id = models.IntegerField(null=True, blank=True)
    chat_id = models.BigIntegerField()
    jadval_sana = models.DateField()
    haftalik = models.BooleanField(default=False)
    qabul_qilindi = models.BooleanField(default=False)
    yuborilgan_vaqt = models.DateTimeField(auto_now_add=True)
    qabul_vaqti = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-yuborilgan_vaqt']

    def __str__(self):
        tur = 'Haftalik' if self.haftalik else 'Kunlik'
        holat = '✅' if self.qabul_qilindi else '⏳'
        return f"{holat} {tur} — {self.jadval_sana}"
