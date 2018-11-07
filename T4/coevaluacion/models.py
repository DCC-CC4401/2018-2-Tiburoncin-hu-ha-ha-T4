from django.db import models
from datetime import datetime


class User(models.Model):
    email = models.CharField(max_length=50)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    rut = models.CharField(max_length=20, unique=True, primary_key=True)
    password = models.CharField(max_length=50)

    ADMIN = 'AD'
    NATURAL_PERSON = 'NP'
    USER_TYPE = (
        (ADMIN, 'Admin'),
        (NATURAL_PERSON, 'NaturalPerson'),
    )
    user_type = models.CharField(max_length=2, choices=USER_TYPE,
                                 default=NATURAL_PERSON,)

    def __str__(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def not_admin(self):
        return self.user_type == self.NATURAL_PERSON


class Course(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=40)
    section_number = models.IntegerField(default=1)
    year = models.IntegerField(default=datetime.now().year)

    PRIMAVERA = 'Primavera'
    OTONO = 'Otoño'
    SEMESTER = (
        (PRIMAVERA, PRIMAVERA),
        (OTONO, OTONO),
    )
    semester = models.CharField(max_length=9, choices=SEMESTER)
    members = models.ManyToManyField(User, through='UserInCourse')

    def __str__(self):
        return "%s-%s, %s %s" % (self.code, self.section_number,
                                 self.semester, self.year)

    class Meta:
        unique_together = (('code', 'section_number', 'year', 'semester'),)


class UserInCourse(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    PROFESOR = 'Profesor'
    AUXILIAR_TEACHER = 'Profesor auxiliar'
    AYUDANTE = 'Ayudante'
    ESTUDIANTE = 'Estudiante'
    ROL = (
        (PROFESOR, PROFESOR),
        (AUXILIAR_TEACHER, AUXILIAR_TEACHER),
        (AYUDANTE, AYUDANTE),
        (ESTUDIANTE, ESTUDIANTE),
    )
    rol = models.CharField(max_length=17, choices=ROL)

    def __str__(self):
        return "%s; %s (%s)" % (self.member, self.course, self.rol)

    class Meta:
        unique_together = (('member', 'course'),)


class Group(models.Model):
    name = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    members = models.ManyToManyField(User)

    def __str__(self):
        return "%s (%s)" % (self.name, self.course)

    class Meta:
        unique_together = (("name", "course"),)


class Question(models.Model):
    question = models.TextField()
    GRADE = 'Grade'
    FREE = 'Free'
    QUESTION_TYPE = (
        (GRADE, GRADE),
        (FREE, FREE),
    )
    question_type = models.CharField(max_length=5, choices=QUESTION_TYPE)

    def __str__(self):
        return "(%s) %s" % (self.question_type, self.question[:10])


class CoEvaluation(models.Model):
    coev_identifier = models.CharField(max_length=40, default='Co-evaluacion',
                                       blank=True)
    init_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(default=datetime.max)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question)

    @property
    def open(self):
        return self.init_date < datetime.now() < self.end_date

    def __str__(self):
        return "%s (%s)" % (self.coev_identifier, self.course)


class Response(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    coevaluation = models.ForeignKey(CoEvaluation, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    coevaluated = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.CharField(max_length=40)

    def __str__(self):
        return "%s (%s) respondida por %s" % (self.question, self.response, self.student)

