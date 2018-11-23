from django.db import models
from datetime import datetime
from django.contrib.auth.models import User as Auth_User
from django.utils import timezone


class User(models.Model):
    user = models.OneToOneField(Auth_User, on_delete=models.CASCADE)
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
        return "%s, %s (%s)" % (self.last_name, self.first_name, self.user_type)

    def not_admin(self):
        return self.user_type == self.NATURAL_PERSON


class NamesPerCode(models.Model):
    code = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=40)

    def __str__(self):
        return "%s: %s" % (self.name, self.code)


class Course(models.Model):
    code = models.ForeignKey(NamesPerCode, on_delete=models.CASCADE)
    # code = models.CharField(max_length=6)
    section_number = models.IntegerField(default=1)
    year = models.IntegerField(default=datetime.now().year)

    SPRING = 2
    FALL = 1
    SEMESTER = (
        (SPRING, "Primavera"),
        (FALL, "Otoño"),
    )
    semester = models.IntegerField(choices=SEMESTER)
    date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        if self.semester == 1:
            sem = "Otoño"
        else:
            sem = "Primavera"
        return "%s-%s %s %s, %s" % (self.code.code, self.section_number,
                                    self.code.name, self.year, sem)

    class Meta:
        unique_together = (('code', 'section_number', 'year', 'semester'),)


class Question(models.Model):
    id = models.IntegerField(primary_key=True)
    GRADE = 'Grade'
    FREE = 'Free'
    QUESTION_TYPE = (
        (GRADE, GRADE),
        (FREE, FREE),
    )
    question_type = models.CharField(max_length=5, choices=QUESTION_TYPE)
    question = models.TextField()

    def __str__(self):
        return "%s: (type %s) %s" % (self.id, self.question_type, self.question[:10])


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
    active = models.BooleanField(default=True)

    def __str__(self):
        return "%s; %s (%s)" % (self.member, self.course, self.rol)

    class Meta:
        unique_together = (('member', 'course'),)


class Group(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "%s (%s): %s" % (self.name, self.course, self.member)

    class Meta:
        unique_together = (("course", "name", "member", "active"),)


class CoEvaluation(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, default='Co-evaluacion')
    # date_start = datetime.now(tz=timezone.get_current_timezone())
    date_end = datetime(year=9999, month=12, day=31,
                        hour=23, minute=59, second=59, microsecond=999999,
                        tzinfo=timezone.get_current_timezone())

    init_date = models.DateTimeField(default=datetime.now(tz=timezone.get_current_timezone()))
    end_date = models.DateTimeField(default=date_end)
    publish = models.BooleanField(default=False)

    def save(self, **kwargs):
        super(CoEvaluation, self).save(**kwargs)
        usersInCourse = UserInCourse.objects.filter(course=self.course)
        for user in usersInCourse:
            if user.rol == "Estudiante":
                answerCoev = AnswerCoEvaluation()
                answerCoev.co_evaluation = self
                answerCoev.user = user
                answerCoev.state = answerCoev.PENDENT
                answerCoev.save()

    def open(self):
        return self.init_date < datetime.now(tz=timezone.get_current_timezone()) \
               and not datetime.now(tz=timezone.get_current_timezone()) > self.end_date

    def __str__(self):
        return "%s, %s (%s - %s)" % (self.course, self.name, self.init_date, self.end_date)


class AnswerCoEvaluation(models.Model):
    user = models.ForeignKey(UserInCourse, on_delete=models.CASCADE)
    co_evaluation = models.ForeignKey(CoEvaluation, on_delete=models.CASCADE)
    # date = models.DateTimeField(default=datetime.now)

    ANSWERED = "Respondida"
    PENDENT = "Pendiente"
    CLOSED = "Cerrado"
    PUBLISH = "Publicada"

    STATE_TYPE = (
        (PENDENT, "Pendiente"),
        (ANSWERED, "Respondida")
    )

    state = models.CharField(max_length=10, choices=STATE_TYPE)

    def __str__(self):
        return "%s: %s (%s)" % (self.user, self.co_evaluation, self.state)

    class Meta:
        unique_together = (("user", "co_evaluation"),)


class QuestionsInCoEvaluation(models.Model):
    co_evaluation = models.ForeignKey(CoEvaluation, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)

    def __str__(self):
        return "%s: %s (weight=%s)" % (self.co_evaluation, self.question, self.weight)

    class Meta:
        unique_together = (("co_evaluation", "question"),)


class AnswerQuestion(models.Model):
    user_who_answer = models.ForeignKey(User, related_name="answer", on_delete=models.CASCADE)
    user_related = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionsInCoEvaluation, on_delete=models.CASCADE)
    response = models.TextField()

    def __str__(self):
        return "%s response %s related to %s" % (self.user_who_answer,
                                                 self.question, self.user_related)

    class Meta:
        unique_together = (("user_who_answer", "user_related", "question"),)


class GradesPerCoEvaluation(models.Model):
    co_evaluation = models.ForeignKey(CoEvaluation, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    grade = models.IntegerField()

    def _str__(self):
        return "%s (%s): %s" % (self.member, self.co_evaluation, self.grade)

    class Meta:
        unique_together = (("co_evaluation", "member"),)