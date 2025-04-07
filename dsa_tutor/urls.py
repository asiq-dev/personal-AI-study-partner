
from django.urls import path
from .views import HomeView, create_tutor, list_tutors, chat_view

urlpatterns = [
    path('<int:tutor_id>/', chat_view, name='home'),
    path('list/', list_tutors, name='tutors_list'),
    path('create/', create_tutor, name='create_tutor'),
]
