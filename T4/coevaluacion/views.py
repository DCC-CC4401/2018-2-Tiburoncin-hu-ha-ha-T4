from django.shortcuts import render


def login(request):
    return render(request, 'login.html')


def home(request):
    return render(request, 'home-vista-alumno.html')


def profile(request):
    return render(request, 'perfil-vista-dueno.html')


def course(request):
    return render(request, 'curso-vista-docente.html')


def coevaluation(request):
    return render(request, 'coevaluacion-vista-alumno.html')
