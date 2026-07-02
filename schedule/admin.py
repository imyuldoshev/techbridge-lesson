from django.contrib import admin

from .models import Dastur, Lesson, Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['ism', 'telefon', 'mutaxassislik', 'telegram_id']
    search_fields = ['ism', 'telefon']
    list_filter = ['mutaxassislik']


@admin.register(Dastur)
class DasturAdmin(admin.ModelAdmin):
    list_display = ['fan', 'dars_raqami', 'sarlavha']
    list_filter = ['fan']
    search_fields = ['sarlavha']
    ordering = ['fan', 'dars_raqami']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['fan_nomi', 'guruh', 'joriy_dars', 'ustoz', 'hafta_kuni', 'hafta_turi', 'boshlanish_vaqti', 'dars_raqami', 'xona', 'faol']
    list_filter = ['hafta_kuni', 'hafta_turi', 'fan_nomi', 'ustoz', 'faol']
    search_fields = ['fan_nomi', 'mavzu', 'ustoz__ism', 'guruh']
    autocomplete_fields = ['ustoz']
    date_hierarchy = 'yaratilgan_sana'
    actions = ['faollashtirish', 'faolsizlantirish']
    list_editable = ['joriy_dars']

    @admin.action(description="Tanlanganlarni faollashtirish")
    def faollashtirish(self, request, queryset):
        queryset.update(faol=True)

    @admin.action(description="Tanlanganlarni faolsizlantirish")
    def faolsizlantirish(self, request, queryset):
        queryset.update(faol=False)
