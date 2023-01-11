from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('settings-security', views.settings_security, name='settings-security'),
    path('search', views.search, name='search'),
    path('upload', views.upload, name='upload'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post', views.like_post, name='like-post'),
    path('follow', views.follow, name='follow'),
    path('refresh', views.refresh, name='refresh'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('delete-post', views.delete_post, name='delete-post'),
    path('followings', views.followings, name='followings'),
    path('chat-profile', views.chat_profile, name='chat-profile'),
    path('room/<str:follower>/<str:user>', views.room, name='room'),
    path('send', views.send, name='send'),
    path('getMessages/<str:username>/<str:room>', views.getMessages, name='getMessages'),
    path('comment', views.comment, name='comment'),
]