from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect

from .models import User, UserInCourse, CoEvaluation


def login(request):
    return render(request, 'login.html')


def login_submit(request):

    username = request.POST['rut']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)

    if user is not None:
        auth_login(request, user)
        return redirect('/')
    else:
        messages.warning(request, 'La contraseña ingresada no es correcta o el usuario no existe')
        return redirect('/login')


@login_required
def home(request):
    user = User.objects.get(user=request.user)
    user_in_course = UserInCourse.objects.filter(member=user)
    coevs = CoEvaluation.objects.filter(course=0)
    for uic in user_in_course:
        coevs = coevs | CoEvaluation.objects.filter(course=uic.course)
    context = {'user': user,
               'userInCourse': user_in_course,
               'coevs': coevs}

    return render(request, 'home-vista-alumno.html', context)


def user_context(request):
    current_user = User.objects.get(user=request.user)
    context = {'first_name': current_user.first_name,
               'last_name': current_user.last_name,
               'rut': current_user.user.username,
               'mail': current_user.email}

    return context


def logout(request):
    auth_logout(request)
    return redirect('/')


def profile(request):
    return render(request, 'perfil-vista-dueno.html')


def course(request):
    return render(request, 'curso-vista-docente.html')

@login_required
def coevaluation(request, coev_id):
    context = {'id' : 2}
    return render(request, 'coevaluacion-vista-alumno.html', context)
