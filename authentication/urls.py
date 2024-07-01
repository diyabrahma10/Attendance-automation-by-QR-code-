from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('registerProf', views.registerProf, name="registerProf"),
    path('loginProf', views.loginProf, name="loginProf"),
    path('logoutProf', views.logoutProf, name="logoutProf"),
    path('activate/<uidb64>/<token>', views.activate, name = "activate"),
    path('qrCodeForm', views.qrCodeForm, name="qrCodeForm"),
]
