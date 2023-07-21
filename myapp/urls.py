from django.urls import path
from . import views


app_name = 'myapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('create_post', views.create_post, name='create_post'),
    path('like-post/', views.like_post, name='like_post'),
    path('profile/', views.profile, name='profile'),
    path('upload_profile_picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('delete_post/', views.delete_post, name='delete_post'),
    path('notifications/', views.notification_view, name='notifications'),
    path('post_detail/<int:post_id>/', views.post_detail, name='post_detail'),
    path('other_profile/<str:username>/', views.other_profile, name='other_profile'),
    path('comments/<int:post_id>/', views.comments, name='comments'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('chat-rooms/', views.chat_rooms, name='chat_rooms'),
    path('chat-select-user/', views.chat_select_user, name='chat_select_user'),
    path('<str:slug>/', views.chat_room, name='room'),
    
]
