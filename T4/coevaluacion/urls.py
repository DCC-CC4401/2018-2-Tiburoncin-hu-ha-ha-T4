from django.conf.urls import url

from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.login, name='login'),
    path('login/submit/', views.login_submit, name='login_submit'),
    path('logout/', views.logout, name='logout'),
    path('', views.home, name='home'),
    path('profile/<str:rut>', views.profile, name='profile'),
    path('<int:year>/<int:semester>/<str:code>/<int:section>', views.course, name='course'),
    path('<int:year>/<int:semester>/<str:code>/<int:section>/peer_assessment/<int:id>',
         views.peer_assessment, name='peer_assessment'),
    path('answer_coevaluation/', views.answer_coevaluation, name='answer_coevaluation'),
]
