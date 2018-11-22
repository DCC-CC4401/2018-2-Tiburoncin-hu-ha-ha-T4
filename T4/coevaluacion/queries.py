from .models import *
from django.db.models.query import QuerySet

'''
Here we define some custom queries to be used in our application
'''


def course_name(course: Course, names: QuerySet):
    match = names.filter(code=course.code)
    if len(match):
        raise ValueError("A code has more than 1 name")
    return names.filter(code=course.code)[0].name


def results_coev(coev: CoEvaluation, user: User, AnswerCoEvaluation: QuerySet):
    questions = QuestionsInCoEvaluation.objects.filter(co_evaluation=coev, weight__gt=0)
    r = 0.0
    n = len(questions)
    for q in questions:
        members = AnswerQuestion.objects.filter(user_related=user, question=q.question)
        m = len(members)
        l = 0.0
        for m in members:
            l += m.response * q.weight * 1.0
        l /= m
        r += l

    return r/n



# def has_answered(co_evaluation: CoEvaluation):
#     ruts = UserActionOnCoEvaluation.objects.filter(action_type='Responde',
#                                                    co_evaluation=co_evaluation).values_list('user')
#     return User.objects.filter(rut__in=ruts)
#
#
# def has_not_answered(co_evaluation: CoEvaluation):
#
#     #  get all the students in the course (their RUT)
#     students = UserInCourse.objects.filter(course=co_evaluation.course,
#                                            rol='Estudiante').values_list('member')
#
#     #  get all the users who has answered the coevaluation
#     users = UserActionOnCoEvaluation.objects.filter(action_type='Responde',
#                                                     co_evaluation=co_evaluation).values_list('user')
#
#     # get the RUT of students who hasn't answered the questions
#     ruts = students.difference(users)
#
#     return User.objects.filter(rut__in=ruts)









