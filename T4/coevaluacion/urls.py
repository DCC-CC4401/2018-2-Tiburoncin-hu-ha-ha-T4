from django.conf.urls import url

from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.login, name='login'),
    path('login/submit/', views.login_submit, name='login_submit'),
    path('logout/', views.logout, name='logout'),
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('course/', views.course, name='course'),
    path('coevaluation/<int:coev_id>', views.coevaluation, name='coevaluation'),
]
