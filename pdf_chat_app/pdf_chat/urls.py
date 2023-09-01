from django.urls import path
from pdf_chat import views

urlpatterns = [
    path("" , views.home ,  name = 'home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout' , views.logout_user , name='logout'),
    path('upload/', views.pdf_upload_view, name='upload'),
    path('chat/', views.chat_view, name='chat'),
    path('end_chat/', views.end_chat_view, name='end_chat')
]