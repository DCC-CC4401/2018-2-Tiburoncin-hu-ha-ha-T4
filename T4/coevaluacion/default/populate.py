from ..models import *
from datetime import datetime, time, date
from django.utils import timezone

'''
script that is going to be used to populate the data base when it's empty.
The population will be small, using only 10 users, 10 coevaluations and 10 courses, 
creating the rest of the data base using this and some other fields

To populate just run the function populate()
It's recommended to run before the file clear.py
'''


def populate():
    create_user()
    create_course()


# user
def create_user():
    first_names = ['name' + str(i) for i in range(1, 11)]
    last_names = ['second' + str(i) for i in range(1, 11)]
    email = ['email{}@gmail.com'.format(i) for i in range(1, 11)]
    password = ['123456' + str(i) for i in range(1, 11)]
    user_type = ['AD'] + ['NP'] * 9
    rut = ["11.23{}.444-2".format(i) for i in range(0, 5)] + \
          ["22.23{}.111-1".format(i) for i in range(0, 5)]
    for f, l, e, p, u, r in zip(first_names, last_names, email, password, user_type, rut):
        tmp = User()
        tmp.email = e
        tmp.first_name = f
        tmp.last_name = l
        tmp.rut = r
        tmp.password = p
        tmp.user_type = u
        tmp.save()


# noinspection PyTypeChecker
def create_datetime(dtime, htime):
    a_date = date(dtime[0], dtime[1], dtime[2])
    aware_time = time(htime[0], htime[1], htime[2], tzinfo=timezone.get_current_timezone())
    return datetime.combine(a_date, aware_time)


# course
def create_course():
    code = [4000 + i for i in range(0, 7)] + [4001, 4002, 4004]
    section = [1] * 7 + [2] * 3
    year = [2018] * 10
    semester = ["Primavera"] * 2 + ["Otoño"] * 4 + ["Primavera"] * 3 + ["Otoño"]
    days = [[i, 10, 23] for i in [1, 4, 4, 5, 7, 7, 7, 7, 10, 11]]
    hours = [[8, i, 11] for i in range(0, 10)]
    date = [create_datetime(days[i], hours[i]) for i in range(0, 10)]

    for c, sec, y, sem, d in zip(code, section, year, semester, date):
        tmp = Course()
        tmp.code = c
        tmp.section_number = sec
        tmp.year = y
        tmp.semester = sem
        tmp.date = d
        tmp.save()