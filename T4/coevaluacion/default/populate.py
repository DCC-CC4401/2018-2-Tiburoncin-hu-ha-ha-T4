from ..models import *
from django.contrib.auth.models import User as Auth_User
from datetime import datetime, time, date
from django.utils import timezone
from ..queries import grade_in_coev

'''
script that is going to be used to populate the data base when it's empty.
The population will be small, using only 10 users, 10 coevaluations and 10 courses, 
creating the rest of the data base using this and some other fields

To populate just run the function populate() on manage.py shell
It's recommended to run before the file clear.py.

To run this file, on the manage shell do:

In[]: from coevaluacion.default.populate import populate
In[]: populate()
'''


def populate():
    admin_user = Auth_User.objects.create_superuser(username='admin', password='tiburoncinadmin', email='admin@admin.cl')
    admin_user.save()
    users = create_user()
    codes = names_per_code()
    courses = create_course(codes)
    questions = question()
    usr_course = user_in_course(courses, users)
    groups = group(usr_course)
    coevs = coevaluation(courses)
    q_in_coev = question_in_coev(coevs, questions)
    _ = answer_Question(usr_course, questions)
    _ = grades_per_coev(usr_course)


# user
def create_user():
    first_names = ['name' + str(i) for i in range(1, 11)]
    last_names = ['second' + str(i) for i in range(1, 11)]
    email = ['email{}@gmail.com'.format(i) for i in range(1, 11)]
    password = ['123456' + str(i) for i in range(1, 11)]
    user_type = ['AD'] + ['NP'] * 9
    rut = ["11.23{}.444-2".format(i) for i in range(0, 5)] + \
          ["22.23{}.111-1".format(i) for i in range(0, 5)]
    table = []
    for f, l, e, p, u, r in zip(first_names, last_names, email, password, user_type, rut):
        user = Auth_User.objects.create_user(username=r, password=p)
        tmp = User()
        tmp.user = user
        tmp.email = e
        tmp.first_name = f
        tmp.last_name = l
        tmp.rut = r
        tmp.password = p
        tmp.user_type = u
        table.append(tmp)
        tmp.save()
    return table


# noinspection PyTypeChecker
def create_datetime(dtime, htime):
    a_date = date(dtime[0], dtime[1], dtime[2])
    aware_time = time(htime[0], htime[1], htime[2], tzinfo=timezone.get_current_timezone())
    return datetime.combine(a_date, aware_time)


# course
code = [4000 + i for i in range(0, 7)] + [4001, 4002, 4004]


# code names
def names_per_code():
    names = ["curso" + str(i) for i in range(0, 7)]
    table = []
    for c, n in zip(code[:7], names):
        tmp = NamesPerCode()
        tmp.code = c
        tmp.name = n
        table.append(tmp)
        tmp.save()
    return table


def create_course(names_code):
    section = [1] * 7 + [2] * 3
    year = [2018] * 10
    semester = [2] * 2 + [1] * 4 + [2] * 3 + [1]
    days = [[2018, i, 23] for i in [1, 4, 4, 5, 7, 7, 7, 7, 10, 11]]
    hours = [[8, i, 11] for i in range(0, 10)]
    date = [create_datetime(days[i], hours[i]) for i in range(0, 10)]
    code = []
    for i in range(len(names_code)):
        code.append(names_code[i])

    code.append(names_code[2])
    code.append(names_code[3])
    code.append(names_code[5])
    table = []
    for c, sec, y, sem, d in zip(code, section, year, semester, date):
        tmp = Course()
        tmp.code = c
        tmp.section_number = sec
        tmp.year = y
        tmp.semester = sem
        tmp.date = d
        table.append(tmp)
        tmp.save()
    return table


# code names
# def names_per_code():
#     names = ["curso" + str(i) for i in range(0, 7)]
#     table = []
#     for c, n in zip(code[:7], names):
#         tmp = NamesPerCode()
#         tmp.code = c
#         tmp.name = n
#         table.append(tmp)
#         tmp.save()
#     return table


# question
def question():
    ids = [i for i in range(0, 10)]
    question_type = ["Grade"] * 2 + ["Free"] * 3 + ["Grade"] * 5
    substring_texts = ["asdgb", "blahblah", "Tiburoncin!", "Nanana-", "huhahuha"]
    question_text = [substring_texts[i%5] * 5 for i in range(0, 10)]
    table = []
    for i, t, q in zip(ids, question_type, question_text):
        tmp = Question()
        tmp.id = i
        tmp.question_type = t
        tmp.question = q
        table.append(tmp)
        tmp.save()
    return table


# user in course
def user_in_course(table_courses, table_users):
    members = []
    courses = []
    j = 1
    for i in [0, 3, 6, 4, 9, 8]:
        k = 0
        while k < 7:
            if table_users[j].not_admin():
                members.append(table_users[j])
                courses.append(table_courses[i])
                k += 1
            j = (j + 1)% 10

    l = len(courses)
    rol_of_one_course = ["Profesor", "Profesor auxiliar"] + ["Estudiante"] * 5
    rol = rol_of_one_course * 6
    active = [False] * 7 * 2 + [True] * 7 * 4
    table = []
    for m, c, r, a in zip(members, courses, rol, active):
        tmp = UserInCourse()
        tmp.member = m
        tmp.course = c
        tmp.rol = r
        tmp.active = a
        table.append(tmp)
        tmp.save()
    return table


# groups
def group(table_users_in_course):
    courses = []
    members = []
    for uc in table_users_in_course:
        if uc.rol == "Estudiante":
            courses.append(uc.course)
            members.append(uc.member)

    name = []
    i = 0
    while i < len(courses):
        c = courses[i]
        j = 0
        while i < len(courses) and courses[i] == c:
            name.append("grupo" + str(j))
            j = (j+1) % 2
            i += 1
    # generate a duplicated members wo change group, and one who delete
    nwc = [11, 10] # i know that these are students
    courses.append(courses[nwc[0]])
    courses.append(courses[nwc[1]])
    members.append(members[nwc[0]])
    members.append(members[nwc[1]])
    name.append(name[nwc[1]])
    name.append(name[nwc[0]])

    active = [True] * len(courses)
    active[nwc[0]] = False
    active[nwc[1]] = False

    table = []
    for c, m, n, a in zip(courses, members, name, active):
        tmp = Group()
        tmp.course = c
        tmp.member = m
        tmp.name = n
        tmp.active = a
        table.append(tmp)
        tmp.save()
    return table


def coevaluation(courses):
    table = []
    days = [[2018, 12, i] for i in [1, 4, 4, 5, 7, 7, 7, 7, 10, 11]]
    hours = [[8, i, 11] for i in range(0, 10)]
    dates = [create_datetime(days[i], hours[i]) for i in range(0, 10)]
    for course, end_date in zip(courses, dates):
        coev = CoEvaluation()
        coev.course = course
        coev.name = "Coev: " + course.code.name
        coev.end_date = end_date
        table.append(coev)
        coev.save()
    return table


def question_in_coev(coevs, questions):
    l = len(questions)
    i = 0
    k = 0
    weights = [23, 45, 12, 35, 5, 35, 45, 44, 67, 43]
    table = []
    for coev in coevs:
        for j in range(0, 10):
            tmp = QuestionsInCoEvaluation()
            if questions[i].question_type == "Grade":
                tmp.weight = weights[k]
                k = (k+2) % 10
            else:
                tmp.weight = 0
            tmp.co_evaluation = coev
            tmp.question = questions[i]
            i = (i+1) % 10
            table.append(tmp)
            tmp.save()
    return table


def answer_Question(users_in_course, questions):

    grades = [7, 7, 7, 6, 5, 6, 7, 5, 6, 7, 6, 6, 4, 7]
    i = 0
    table = []
    for u in users_in_course:
        if u.rol == "Estudiante":
            c = u.course
            n = Group.objects.filter(course=c, member=u.member, active=True)
            if len(n) > 0:
                n = n[0].name
                members = Group.objects.filter(course=c, active=True, name=n)
                coev = CoEvaluation.objects.get(course=c) # we know that there is only 1 per course
                for q in QuestionsInCoEvaluation.objects.filter(co_evaluation=coev):
                    for m in members:
                        if m.member != u.member:
                            tmp = AnswerQuestion()
                            tmp.user_who_answer = u.member
                            tmp.user_related = m.member
                            tmp.question = q
                            if tmp.question.question.question_type == "Grade":
                                tmp.response = str(grades[i])
                                i = (i+1) % len(grades)
                            else:
                                tmp.response = "baia baia"
                            table.append(tmp)
                            tmp.save()
    return table


def grades_per_coev(users_in_course):

    table = []
    for usr in users_in_course:
        coevs = CoEvaluation.objects.filter(course=usr.course)
        for coev in coevs:
            c = UserInCourse.objects.filter(member=usr.member, rol="Estudiante",
                                            course=coev.course).count()
            if c == 1:

                tmp = GradesPerCoEvaluation()
                tmp.grade = int(round(grade_in_coev(usr.member, coev), 1) * 10)
                tmp.co_evaluation = coev
                tmp.member = usr.member
                table.append(tmp)
                tmp.save()
            elif c > 2:
                raise ValueError("a user is repeated in a course!!")
    return table
