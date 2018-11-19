from ..models import *
from django.contrib.auth.models import User as Auth_User
from datetime import datetime, time, date
from django.utils import timezone

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
    courses = create_course()
    _ = names_per_code()
    _ = question()
    _ = user_in_course(courses, users)


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


def create_course():
    section = [1] * 7 + [2] * 3
    year = [2018] * 10
    semester = ["Primavera"] * 2 + ["Otoño"] * 4 + ["Primavera"] * 3 + ["Otoño"]
    days = [[i, 10, 23] for i in [1, 4, 4, 5, 7, 7, 7, 7, 10, 11]]
    hours = [[8, i, 11] for i in range(0, 10)]
    date = [create_datetime(days[i], hours[i]) for i in range(0, 10)]
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
    j = 0
    for i in [0, 3, 6, 4, 9, 8]:
        k = 0
        while k < 7:
            if table_users[j].not_admin() and table_users[j] not in members:
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


# groups, TODO: not working
def group(table_users_in_course):
    courses = []
    members = []
    for uc in table_users_in_course:
        if uc.rol is "Estudiante":
            courses.append(uc.course)
            members.append(uc.member)

    name = []
    i = 0
    while i < len(courses):
        c = courses[i]
        j = 0
        i += 1
        while courses[i] == c:
            name.append("grupo" + str(j))
            j = (j+1) % 3
            i += 1

    # generate a duplicated members wo change group, and one who delete
    number_delete = 4
    number_whos_change = [9, 12]
    courses.append(table_users_in_course[9].course)
    members.append(table_users_in_course[12].member)
    courses.append(table_users_in_course[12].course)
    members.append(table_users_in_course[9].member)







