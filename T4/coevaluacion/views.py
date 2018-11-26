from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, redirect

from .queries import *
from .models import User, UserInCourse, CoEvaluation, Course, \
    AnswerCoEvaluation, GradesPerCoEvaluation, UserInGroup


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

    list_coevs = list()

    is_teacher = False
    for logged_course in logged_courses:
        coevs = CoEvaluation.objects.filter(course=logged_course.course)
        assessments = assessments | coevs
        if logged_course.rol != "Estudiante":
            is_teacher = True
            ansCoev = None
        for coev in coevs:
            if logged_course.rol != "Estudiante":
                ansCoev = None
                ansCoevID = None
            else:
                ansCoev = AnswerCoEvaluation.objects.get(user=logged_course, co_evaluation=coev)
                ansCoevID = ansCoev.id
            list_coevs.append({'coev': coev, 'ansCoev': ansCoev, 'ansCoevID': ansCoevID, 'rol': logged_course.rol,
                               'status': status_coev(logged_course, coev)})

    course_assessments = AnswerCoEvaluation.objects.filter(user=0)
    for logged_course in logged_courses:
        course_assessments = course_assessments | AnswerCoEvaluation.objects.filter(user=logged_course)
    context = {'user': logged_user,
               'is_teacher': is_teacher,
               'userInCourse': logged_courses,
               'coevs': assessments,
               'coevsInCourse': course_assessments,
               'list_coevs': list_coevs}

    return render(request, 'home.html', context)


@login_required
def logout(request):
    auth_logout(request)
    return redirect('/')


@login_required
def profile(request, rut):
    visitor = User.objects.get(user=request.user)

    is_owner = visitor.compare_rut(rut)
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
            visitor_in_course = visitor_courses.filter(course=owner_course.course)[0]
        else:
            visitor_in_course = None

        if (owner_course.course.id,) in list(visitor_courses.values_list("course")) and not visitor_in_course.is_student:
            courses.append({'course': owner_course, 'visitor_rol': visitor_in_course.rol})
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

    context = {
        'user': visitor_user,
        'user_in_course': visitor_in_course,
        'course': requested_course,
        'upper_table': extended_assessments(visitor_in_course, requested_course),
        'is_teacher': is_visitor_teacher(request)}

    # Si el user es docente, se agrega la información de los grupos al contexto
    if not visitor_in_course.is_student:
        groups = Group.objects.filter(course=requested_course)
        users_in_groups = UserInGroup.objects.filter(group__in=groups, active=True)
        active_groups = users_in_groups.values_list("group").distinct()
        active_groups = Group.objects.filter(id__in=active_groups)

        user_in_groups_list = list()
        for group in active_groups:
            group_members = users_in_groups.filter(group=group)

            group_members_list = list()
            for group_member in group_members:
                assessments_in_course = CoEvaluation.objects.filter(course=requested_course)
                grades_list = list()
                for assessment_in_course in assessments_in_course:
                    grades_per_assessment = GradesPerCoEvaluation.objects.get(member=group_member.member,
                                                                              co_evaluation=assessment_in_course)
                    grades_list.append(grades_per_assessment)
                group_members_list.append({'member': group_member.member, 'grades_list': grades_list})

            user_in_groups_list.append({'group': group, 'members': group_members_list})

        context['user_in_groups_list'] = user_in_groups_list

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
    group = UserInGroup.objects.get(member=assessment.user.member, group__course=assessment.co_evaluation.course,
                                    active=True).group
    usersInGroup = UserInGroup.objects.filter(group=group).exclude(member=assessment.user.member)
    questions = QuestionsInCoEvaluation.objects.filter(co_evaluation=assessment.co_evaluation)
    teamMates = list()
    for user in usersInGroup:
        coevaluated = AnswerQuestion.objects.filter(user_who_answer=assessment.user.member,
                                                    user_related=user.member,
                                                    group=group).exists()
        teamMates.append({'teammate': user, 'coevaluated': coevaluated})
    context = {
        'user': logged_user,
        'is_teacher': is_teacher,
        'ansCoev': assessment,
        'group': group,
        'usersInGroup': usersInGroup,
        'teammates': teamMates,
        'questions': questions
    }
    return render(request, 'coevaluacion-vista-alumno.html', context)

@login_required
def answer_coevaluation(request):
    if request.POST:
        ansCoevID = request.POST['ansCoev-id']
        ansCoev = AnswerCoEvaluation.objects.get(id=ansCoevID)

        ans = request.POST['bla']

        userWhoAnswer = User.objects.get(rut=request.POST['userWhoAnswer-rut'])
        userAnswered = User.objects.get(rut=request.POST['userAnswered-rut'])



        messages.warning(request,'bla')
        return redirect('/'+str(ansCoev.co_evaluation.course.year)
                        +'/'+str(ansCoev.co_evaluation.course.semester)
                        +'/'+str(ansCoev.co_evaluation.course.code.code)
                        +'/'+str(ansCoev.co_evaluation.course.section_number)
                        +'/peer_assessment'
                        +'/'+str(ansCoev.id))