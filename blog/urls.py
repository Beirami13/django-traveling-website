from django.urls import path
from . import views

urlpatterns = [
    path('add_memory', views.memory_create, name='memory_create'),
    path('<int:pk>/edit', views.memory_edit, name='memory_edit'),
    path('<int:pk>/delete', views.memory_delete, name='memory_delete'),
    path('question/<int:question_id>/answer', views.answer_question, name='answer_question'),
]