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
]
