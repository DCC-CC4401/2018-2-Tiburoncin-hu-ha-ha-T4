from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from coevaluacion.models import User


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

    return render(request, 'login.html')


@login_required
def home(request):
    context = user_context(request)

    return render(request, 'home-vista-alumno.html', context)

def user_context(request):
    current_user = User.objects.get(user=request.user)
    context = {'first_name': current_user.first_name,
               'last_name': current_user.last_name,
               'rut' : current_user.user.username,
               'mail' : current_user.email}

    return context

def logout(request):
    auth_logout(request)
    return redirect('/')


def profile(request):
    return render(request, 'perfil-vista-dueno.html')


def course(request):
    return render(request, 'curso-vista-docente.html')


def coevaluation(request):
    return render(request, 'coevaluacion-vista-alumno.html')
