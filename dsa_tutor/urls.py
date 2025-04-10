
from django.urls import path
from .views import CreateTutorView, list_tutors, chat_view, chat

urlpatterns = [
    path('<int:tutor_id>/', chat_view, name='chat_view'),
    path('list/', list_tutors, name='tutors_list'),
    path('create/', CreateTutorView.as_view(), name='create_tutor'),
    path('chat/', chat, name='chat')
]
