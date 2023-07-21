from django.urls import path

from . import views

app_name = 'chatapp'

urlpatterns = [
    path("", views.rooms, name="rooms"),
    path("<str:slug>", views.chat_room, name="chat-room"),
    path('room/<str:slug>/', views.chat_room, name='room'),
]