from django import forms

from .models import Lesson, Teacher


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['ism', 'telegram_id', 'telefon', 'mutaxassislik']

    def clean_ism(self):
        ism = self.cleaned_data.get('ism', '').strip()
        if not ism:
            raise forms.ValidationError("Ism majburiy.")
        return ism

    def clean_telegram_id(self):
        telegram_id = self.cleaned_data.get('telegram_id')
        if not telegram_id:
            return None
        qs = Teacher.objects.filter(telegram_id=telegram_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Bu Telegram ID allaqachon band.")
        return telegram_id


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'ustoz', 'hafta_kuni', 'hafta_turi', 'boshlanish_vaqti', 'tugash_vaqti',
            'dars_raqami', 'fan_nomi', 'mavzu', 'xona', 'guruh', 'faol', 'eslatma',
        ]
        widgets = {
            'boshlanish_vaqti': forms.TimeInput(attrs={'type': 'time'}),
            'tugash_vaqti': forms.TimeInput(attrs={'type': 'time'}),
            'mavzu': forms.Textarea(attrs={'rows': 3}),
            'eslatma': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_dars_raqami(self):
        dars_raqami = self.cleaned_data.get('dars_raqami')
        if dars_raqami is not None and not (1 <= dars_raqami <= 8):
            raise forms.ValidationError("Dars raqami 1 dan 8 gacha bo'lishi kerak.")
        return dars_raqami

    def clean(self):
        cleaned_data = super().clean()
        boshlanish = cleaned_data.get('boshlanish_vaqti')
        tugash = cleaned_data.get('tugash_vaqti')
        if boshlanish and tugash and boshlanish >= tugash:
            raise forms.ValidationError("Boshlanish vaqti tugash vaqtidan oldin bo'lishi kerak.")

        ustoz = cleaned_data.get('ustoz')
        hafta_kuni = cleaned_data.get('hafta_kuni')
        dars_raqami = cleaned_data.get('dars_raqami')
        hafta_turi = cleaned_data.get('hafta_turi') or 'har_doim'
        if ustoz and hafta_kuni and dars_raqami:
            qs = Lesson.objects.filter(ustoz=ustoz, hafta_kuni=hafta_kuni, dars_raqami=dars_raqami)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if hafta_turi == 'har_doim':
                conflict = qs.exists()
            else:
                conflict = qs.filter(hafta_turi__in=['har_doim', hafta_turi]).exists()
            if conflict:
                raise forms.ValidationError(
                    "Bu ustozning shu kunda, shu dars raqamida va shu hafta turida boshqa darsi mavjud."
                )
        return cleaned_data
