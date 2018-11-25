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
    print("Creating Django Admin...")
    admin_user = Auth_User.objects.create_superuser(username='admin', password='tiburoncinadmin', email='admin@admin.cl')
    admin_user.save()
    print("Creating Users...")
    users = create_user()
    print("Creating Course Codes and names...")
    codes = names_per_code()
    print("Creating Courses...")
    courses = create_course(codes)
    print("Creating questions...")
    questions = question()
    print("Putting Users in some Courses...")
    usr_course = user_in_course(courses, users)
    print("Creating Groups per Course...")
    _ = group(courses)
    print("Putting Users in groups...")
    user_in_group(courses)
    print("Creating Co-evaluations per course...")
    coevs = coevaluation(courses)
    print("Creating questions per co-evaluation...")
    _ = question_in_coev(coevs, questions)
    print("Simulating Answer for those questions...")
    _ = answer_Question(usr_course, questions)
    print("Calculating grades in this co-evaluations...")
    _ = grades_per_coev(usr_course)


# user
def create_user():
    first_names = ['name' + str(i) for i in range(1, 11)]
    last_names = ['second' + str(i) for i in range(1, 11)]
    email = ['email{}@gmail.com'.format(i) for i in range(1, 11)]
    password = ['123456' + str(i) for i in range(1, 11)]
    user_type = ['AD'] + ['NP'] * 9
    rut = ["1123{}444-2".format(i) for i in range(0, 5)] + \
          ["2223{}111-1".format(i) for i in range(0, 5)]
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
    section = [1] * 10
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
    for i, j in zip([2, 3, 5], [7, 8, 9]):
        if semester[i] == semester[j]:
            section[j] = 2

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
            if table_users[j].not_admin:
                members.append(table_users[j])
                courses.append(table_courses[i])
                k += 1
            j = (j + 1)% 10

    l = len(courses)
    rol_of_one_course = [UserInCourse.PROFESOR, UserInCourse.AUXILIAR_TEACHER] + \
                        [UserInCourse.ESTUDIANTE] * 5
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


# group
def group(courses):
    # for every course, create 2 groups
    name = []
    course = []
    for c in courses:
        name.append("Este no es un grupo " + str(c.id))
        name.append("Este tampoco :C " + str(c.id))
        course.append(c)
        course.append(c)

    table = []
    for c, n in zip(course, name):
        tmp = Group()
        tmp.course = c
        tmp.name = n
        table.append(tmp)
        tmp.save()
    return table


# groups
def user_in_group(courses):
    groups = []
    members = []
    state = []
    p = courses[3]
    for c in courses:
        usrs = UserInCourse.objects.filter(course=c,
                                           rol=UserInCourse.ESTUDIANTE)
        grps = Group.objects.filter(course=c)
        N = grps.count()
        n = 0
        for u in usrs:
            groups.append(grps[n])
            members.append(u.member)
            state.append(True)
            n = (n+1) % N
    table = []
    for g, m, a in zip(groups, members, state):
        tmp = UserInGroup()
        tmp.group = g
        tmp.member = m
        tmp.active = a
        table.append(tmp)
        tmp.save()

    # change two studen of groups
    c = UserInCourse.objects.filter(rol=UserInCourse.ESTUDIANTE)[5].course  # get some course
    groups = Group.objects.filter(course=c)
    user_groups = UserInGroup.objects.filter(group__in=groups)  # get all the users in groups for that course
    u1 = user_groups[3] # take a member of any of these groups
    # and take another one in a different group
    for u2 in user_groups:
        if u2.group != u1.group:
            break

    u1.change_group(u2.group)
    u2.change_group(u1.group)
    # raise ValueError()

    return None


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
            if questions[i].is_grade:
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
        if u.is_student:
            c = u.course
            possible_groups = Group.objects.filter(course=c)
            user_who_answer = UserInGroup.objects.filter(group__in=possible_groups, member=u.member)
            user_who_answer = user_who_answer.filter(active=True)
            if len(user_who_answer) == 1:
                user_who_answer = user_who_answer[0]
                users_related = UserInGroup.objects.filter(group=user_who_answer.group, active=True)
                coev = CoEvaluation.objects.get(course=c) # we know that there is only 1 per course
                for q in QuestionsInCoEvaluation.objects.filter(co_evaluation=coev):
                    for user_related in users_related:
                        if user_related.member != user_who_answer.member:
                            tmp = AnswerQuestion()
                            tmp.user_who_answer = user_who_answer.member
                            tmp.user_related = user_related.member
                            tmp.question = q
                            tmp.group = user_who_answer.group
                            if tmp.question.question.is_grade:
                                tmp.response = str(grades[i])
                                i = (i+1) % len(grades)
                            else:
                                tmp.response = "baia baia"
                            table.append(tmp)
                            tmp.save()
            else:
                raise ValueError("Problema")
    return table


def grades_per_coev(users_in_course):

    table = []
    for usr in users_in_course:
        coevs = CoEvaluation.objects.filter(course=usr.course)
        for coev in coevs:
            c = UserInCourse.objects.filter(member=usr.member, rol=UserInCourse.ESTUDIANTE,
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
