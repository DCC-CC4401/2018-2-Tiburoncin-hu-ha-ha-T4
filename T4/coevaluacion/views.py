from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect

from .models import User, UserInCourse, CoEvaluation, Course, AnswerCoEvaluation, NamesPerCode


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

    coevsInCourse = AnswerCoEvaluation.objects.filter(user=0)
    for uic in user_in_course:
        coevsInCourse = coevsInCourse | AnswerCoEvaluation.objects.filter(user=uic)
    context = {'user': user,
               'userInCourse': user_in_course,
               'coevs': coevs,
               'coevsInCourse': coevsInCourse}

    return render(request, 'home-vista-alumno.html', context)


@login_required
def logout(request):
    auth_logout(request)
    return redirect('/')


@login_required
def profile(request, rut):
    profile_user = User.objects.get(rut=rut)
    logged_user = User.objects.get(user=request.user)

    owner = (logged_user.rut == rut)

    owner_courses = UserInCourse.objects.filter(member=profile_user)
    logged_courses = UserInCourse.objects.filter(member=logged_user)

    courses = []
    for owner_course in owner_courses:

        visitor_rol = logged_courses.filter(course=owner_course.course)
        visitor_rol = visitor_rol[0].rol if visitor_rol else ""

        if (owner_course.course.id,) in list(logged_courses.values_list("course")) and visitor_rol != "Estudiante":
            courses.append({'course': owner_course, 'visitor_rol': visitor_rol})
        else:
            courses.append({'course': owner_course, 'visitor_rol': None})

    courses = sorted(courses, key=lambda x: (x['course'].course.year, x['course'].course.semester), reverse=True)

    context = {
        'profile_user': profile_user,
        'logged_user': logged_user,
        'owner': owner,
        'courses': courses
    }
    return render(request, 'profile.html', context)


@login_required
def course(request, year, semester, code, section):
    visitor = User.objects.get(user=request.user)
    code_name = NamesPerCode.objects.get(code=code)
    course = Course.objects.get(code=code_name, section_number=int(section),
                                year=int(year), semester=int(semester))
    coevs = CoEvaluation.objects.filter(course=course)
    members = UserInCourse.objects.filter(course=course)
    context = {
        'visitor': visitor,
        'course': course,
        'members': members,
        'coevs': coevs
    }

    if members.filter(member=visitor).count() == 1:
        if members.get(course=course, member=visitor).rol == "Estudiante":
            return render(request, "curso-vista-alumno.html", context)
        else:
            return render(request, "curso-vista-docente.html", context)

    else:
        # can be an admin, but for now, is not accepted
        messages.warning(request, 'No tienes acceso a esta vista')
        return redirect('/')


@login_required
def peer_assessment(request, year, semester, code, section, id):
    user = User.objects.get(user=request.user)
    ansCoev = AnswerCoEvaluation.objects.get(id=id)
    context = {
        'user': user,
        'ansCoev': ansCoev}
    return render(request, 'coevaluacion-vista-alumno.html', context)
