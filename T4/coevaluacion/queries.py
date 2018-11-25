from .models import *
from django.db.models.query import QuerySet

'''
Here we define some custom queries to be used in our application
'''


def mean_point_per_question(user: User, question: QuestionsInCoEvaluation):
    """
    calculate the mean points obtained by a user in an specific question

    :param user: user instance
    :param question: question instance
    :return: the mean points (a float)
    """
    ans_quest = AnswerQuestion.objects.filter(question=question, user_related=user)
    t = 0.0
    for ans in ans_quest:
        t += int(ans.response)
    t /= ans_quest.count()
    return t


def grade_in_coev(user: User, coev: CoEvaluation):
    """
    query to get the resulting grade of a user ("Estudiante") related
    to a specific coevaluation

    :param user: user instance
    :param coev: qcoevaluation instance
    :return: the total grade (a float)
    """
    quests = QuestionsInCoEvaluation.objects.filter(co_evaluation=coev)
    s = 0
    w_total = 0
    for q in quests:
        if q.question.question_type == "Grade":
            t = mean_point_per_question(user, q)
            s += t * q.weight
            w_total += q.weight
    return s/w_total


def status_coev(user_in_course: UserInCourse, coev: CoEvaluation):
    """
    compute the relative status of a coevaluation for an specific user,
    if the user is an "Estudiante" in the course of the coevaluation then
    the status can be ("Respondida", "Pendiente",  "Publicada"  or "Cerrada")
    if the user is part of the "equipo docente" then the status can be
    ("Abierta", "Cerrada", "Publicada")

    :param user_in_course: the user instance
    :param coev: the coevaluation instance
    :return: the status (a string)
    """
    if coev.publish:
        status = "Publicada"
    else:
        if user_in_course.rol == "Estudiante":
            status = AnswerCoEvaluation.objects.get(user=user_in_course,
                                                    co_evaluation=coev).state
            if status == "Pendiente" and not coev.open():
                status = "Cerrada"
        else:
            status = "Abierta" if coev.open() else "Cerrada"

    return status


def latest_coev_with_status(user: User):
    """
    query to get the last 10 coevaluations related to a user with the respective relative status
    which can be ("Abierta", "Cerrada", "Publicada", "Respondida", "Pendiente")
    :param user: the user
    :return: the clast 10 coevaluations and their relative status
    """
    usr_in_crs =UserInCourse.objects.filter(member=user)
    vals = usr_in_crs.values_list("course")
    usr_courses = Course.objects.filter(id__in=vals)

    related_coevs = CoEvaluation.objects.filter(course__in=usr_courses)
    related_coevs = related_coevs.order_by("-end_date")
    status = []
    for i in range(related_coevs.count()):
        usr_in_course = UserInCourse.objects.get(course=related_coevs[i].course,
                                                 member=user)
        status.append(status_coev(usr_in_course, related_coevs[i]))

    return related_coevs, status


def ten_latest_coev(user: User):
    related_coevs, status = latest_coev_with_status(user)
    if related_coevs.count() < 10:
        return related_coevs, status
    else:
        return related_coevs[:10], status[:10]


def course_base_query(request, year, semester, code, section):
    visitor = User.objects.get(user=request.user)
    code_name = NamesPerCode.objects.get(code=code)
    course = Course.objects.get(code=code_name, section_number=int(section),
                                year=int(year), semester=int(semester))
    coevs = CoEvaluation.objects.filter(course=course)
    members = UserInCourse.objects.filter(course=course)
    visitor_member = members.filter(member=visitor)
    context = {'user': visitor, 'course': course, 'members': members,
               "usrcourse": visitor_member[0], 'coevs': coevs}
    return context, visitor_member.count()


def course_student_query(context):
    itervar = []
    for coev in context["coevs"]:
        status = AnswerCoEvaluation.objects.get(user=context["usrcourse"], co_evaluation=coev)
        itervar.append({"coev": coev, "status": status})
    context["itervar"] = itervar
    return context


def course_teacher_query(context):
    groups = Group.objects.filter(course=context["course"])
    actives = groups.filter(active=True).values_list("name").distinct()
    itervar = []
    for i in range(actives.count()):
        members = groups.filter(name=actives[i])
        itervar.append({"active": actives[i], "i": i, "members": members})
    context["groups"] = groups
    context["itervar"] = itervar
    return context










