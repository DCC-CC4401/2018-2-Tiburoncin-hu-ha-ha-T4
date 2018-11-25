from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseNotFound
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
    visitor = User.objects.get(user=request.user)

    is_owner = (visitor.rut == rut)
    visitor_courses = UserInCourse.objects.filter(member=visitor)
    is_teacher = is_visitor_teacher(request)

    try:
        profile_user = User.objects.get(rut=rut)
    except User.DoesNotExist:
        context = {
            'user': visitor,
            'is_teacher': is_teacher,
        }
        if not is_teacher:
            return render(request, "403.html", context)
        else:

            return render(request, "404.html", context)

    owner_courses = UserInCourse.objects.filter(member=profile_user)

    courses = list()

    is_owners_teacher = False
    for owner_course in owner_courses:
        is_common_course = len(visitor_courses.filter(course=owner_course.course)) != 0

        if is_common_course:
            visitor = visitor_courses.filter(course=owner_course.course)[0]
        else:
            visitor = None

        if (owner_course.course.id,) in list(visitor_courses.values_list("course")) and not visitor.is_student:
            courses.append({'course': owner_course, 'visitor_rol': visitor.rol})
            is_owners_teacher = True
        else:
            courses.append({'course': owner_course, 'visitor_rol': None})

    if not is_owners_teacher:
        return HttpResponseForbidden()

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
        'user': visitor,
        'is_teacher': is_teacher,
        'is_owner': is_owner,
        'courses': courses
    }
    return render(request, 'profile.html', context)


@login_required
def course(request, year, semester, code, section):
    visitor_user = User.objects.get(user=request.user)

    # Si el curso no existe, retorna error 404
    try:
        requested_course = Course.objects.get(code=NamesPerCode.objects.get(code=code),
                                              section_number=int(section),
                                              year=int(year),
                                              semester=int(semester))
    except Course.DoesNotExist:
        return render(request, "404.html", {'user': visitor_user, 'is_teacher': is_visitor_teacher(request)})

    members = UserInCourse.objects.filter(course=requested_course)

    # Si no pertenece al curso, no puede ver la pagina del mismo
    if members.filter(member=visitor_user).count() == 0:
        return render(request, "403.html", {'user': visitor_user, 'is_teacher': is_visitor_teacher(request)})

    visitor_in_course = members.get(member=visitor_user)

    upper_table = list()
    assessments = CoEvaluation.objects.filter(course=requested_course)
    for assessment in assessments:
        try:
            status = AnswerCoEvaluation.objects.get(user=visitor_in_course, co_evaluation=assessment)
        except AnswerCoEvaluation.DoesNotExist:
            status = None
        upper_table.append({'assessment': assessment, 'status': status})

    context = {
        'user': visitor_user,
        'user_in_course': visitor_in_course,
        'course': requested_course,
        'members': members,
        'upper_table': upper_table,
        'is_teacher': is_visitor_teacher(request)}

    if not visitor_in_course.is_student:
        groups = Group.objects.filter(course=requested_course)
        active_groups = groups.filter(active=True).values_list("name").distinct()

        groups_list = list()
        for group in active_groups:
            group_members = groups.filter(name=group[0])

            group_members_list = list()
            for group_member in group_members:
                group_members_list.append(group_member.member)

            groups_list.append({'name': group[0], 'members': group_members_list})

        context['groups_list'] = groups_list

    return render(request, "course.html", context)


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
