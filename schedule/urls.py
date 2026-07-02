from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/add/', views.teacher_form_view, name='teacher_add'),
    path('teachers/edit/<int:pk>/', views.teacher_form_view, name='teacher_edit'),
    path('teachers/delete/<int:pk>/', views.teacher_delete, name='teacher_delete'),

    path('lessons/', views.lesson_list, name='lesson_list'),
    path('lessons/add/', views.lesson_form_view, name='lesson_add'),
    path('lessons/edit/<int:pk>/', views.lesson_form_view, name='lesson_edit'),
    path('lessons/delete/<int:pk>/', views.lesson_delete, name='lesson_delete'),
    path('lessons/export/', views.lesson_export_excel, name='lesson_export_excel'),

    path('schedule/', views.schedule_view, name='schedule'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('dastur/', views.dastur_view, name='dastur'),
]
