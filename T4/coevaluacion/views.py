from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .queries import *
from .models import User, UserInCourse, CoEvaluation, Course, AnswerCoEvaluation, GradesPerCoEvaluation


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
    logged_user = User.objects.get(user=request.user)
    logged_courses = UserInCourse.objects.filter(member=logged_user)
    assessments = CoEvaluation.objects.filter(course=0)

    is_teacher = False
    for logged_course in logged_courses:
        assessments = assessments | CoEvaluation.objects.filter(course=logged_course.course)
        if logged_course.rol != "Estudiante":
            is_teacher = True

    course_assessments = AnswerCoEvaluation.objects.filter(user=0)
    for logged_course in logged_courses:
        course_assessments = course_assessments | AnswerCoEvaluation.objects.filter(user=logged_course)
    context = {'user': logged_user,
               'is_teacher': is_teacher,
               'userInCourse': logged_courses,
               'coevs': assessments,
               'coevsInCourse': course_assessments}

    return render(request, 'home.html', context)


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

    is_teacher = False
    for logged_course in logged_courses:
        if logged_course.rol != "Estudiante":
            is_teacher = True
            break

    courses = list()

    for owner_course in owner_courses:
        visitor_rol = logged_courses.filter(course=owner_course.course)
        visitor_rol = visitor_rol[0].rol if visitor_rol else ""
        print(owner_course.course.code.name)
        if (owner_course.course.id,) in list(logged_courses.values_list("course")) and visitor_rol != "Estudiante":
            courses.append({'course': owner_course, 'visitor_rol': visitor_rol})
        else:
            courses.append({'course': owner_course, 'visitor_rol': None})

    courses = sorted(courses, key=lambda x: (x['course'].course.year, x['course'].course.semester), reverse=True)

    grades_per_assessment = GradesPerCoEvaluation.objects.filter(member=profile_user)
    for i in range(len(courses)):
        grades = list()
        for grade in grades_per_assessment:
            if grade.co_evaluation.course == courses[i]['course'].course:
                grades.append(grade)
        courses[i]['grades'] = grades
        courses[i]['course_index'] = i

    context = {
        'profile_user': profile_user,
        'user': logged_user,
        'is_teacher': is_teacher,
        'owner': owner,
        'courses': courses
    }
    return render(request, 'profile.html', context)


@login_required
def course(request, year, semester, code, section):
    context, c = course_base_query(request, year, semester, code, section)
    if c == 1:
        if context["usrcourse"].is_student:
            context = course_student_query(context)
            return render(request, "curso-vista-alumno.html", context)
        else:
            context = course_teacher_query(context)
            return render(request, "curso-vista-docente.html", context)

    else:
        # can be an admin, but for now, is not accepted
        messages.warning(request, 'No tienes acceso a esta vista')
        return redirect('/')


@login_required
def peer_assessment(request, year, semester, code, section, id):
    logged_user = User.objects.get(user=request.user)
    logged_courses = UserInCourse.objects.filter(member=logged_user)

    is_teacher = False
    for logged_course in logged_courses:
        if logged_course.rol != "Estudiante":
            is_teacher = True
            break

    assessment = AnswerCoEvaluation.objects.get(id=id)
    context = {
        'user': logged_user,
        'is_teacher': is_teacher,
        'ansCoev': assessment,
    }
    return render(request, 'coevaluacion-vista-alumno.html', context)
