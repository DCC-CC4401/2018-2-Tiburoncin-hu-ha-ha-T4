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
        return "%s, %s" % (self.last_name, self.first_name)

    @property
    def get_simple_rut(self):
        return str(self.rut)[:-2]

    @property
    def get_checker_digit(self):
        return str(self.rut)[-1]

    @property
    def not_admin(self):
        return self.user_type == self.NATURAL_PERSON

    def compare_rut(self, rut):
        return str(self.rut) == str(rut)


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

    @property
    def is_grade(self):
        return self.question_type == self.GRADE

    @property
    def is_free(self):
        return self.question_type == self.FREE


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

    @property
    def is_student(self):
        return self.rol == self.ESTUDIANTE

    @property
    def is_assistant_teacher(self):
        return self.rol == self.AUXILIAR_TEACHER

    @property
    def is_assistant(self):
        return self.rol == self.AYUDANTE

    @property
    def is_teacher(self):
        return self.rol == self.PROFESOR

    class Meta:
        unique_together = (('member', 'course'),)


class Group(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return "%s" % (self.name, )

    class Meta:
        unique_together = (("course", "name"),)


class UserInGroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    @property
    def is_active(self):
        return self.active

    def is_alone(self):
        """
        this should check if a member is alone in a group, in that case
        we need to add a new member to this group or delete de group and
        move the student to another group. A member alone in a group should
        be considered as a member who is not in a group.
        """
        raise NotImplementedError()

    def teammates(self):
        """
        here we should get the ACTUAL teammates of a student.
        """
        raise NotImplementedError()

    def change_group(self, group):
        """
        here we can change the actual group of a member,
        this means, set as non active in this group and add
        a new entry in the data base with the member in the new group
        """
        self.active = False
        self.save()

        tmp = UserInGroup()
        tmp.group = group
        tmp.member = self.member
        tmp.active = True
        tmp.save()

    def __str__(self):
        return "%s: %s (%s)" % (self.group, self.member, self.active)

    class Meta:
        unique_together = (("group", "member"),)


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

    OPEN = "Abierta"
    CLOSED = "Cerrada"
    PUBLISH = "Publicada"

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

    @property
    def is_open(self):
        return self.open()

    @property
    def is_closed(self):
        return not self.open()

    @property
    def is_published(self):
        return self.publish

    @property
    def status(self):
        if self.is_open:
            return self.OPEN
        elif self.is_published:
            return self.PUBLISH
        else:
            return self.CLOSED

    @property
    def get_end_date(self):
        tmp = self.end_date.strftime("%H:%M %d/%m/%Y")
        return tmp[:-4] + tmp[-2:]

    @property
    def get_init_date(self):
        tmp = self.init_date.strftime("%H:%M %d/%m/%Y")
        return tmp[:-4] + tmp[-2:]

    def publish_co_evaluation(self):
        """
        ideally here we should declare what happens when a co-evaluation
        is published, this means, calculate the grade of every student and
        store the results in GradesPerCoEvaluation, this is not required yet
        and thus is not implemented but it is declared for completeness.
        """
        raise NotImplementedError()

    def add_question(self, question, weight=1):
        """
        Here we should be able to add a new question to the co-evaluation

        :param question:
        :param weight:
        """
        raise NotImplementedError()

    def remove_question(self, question):
        """
        Here que should be able to remove a question form the co-evaluation

        :param question:
        """
        raise NotImplementedError()

    def __str__(self):
        return "%s, %s (%s - %s)" % (self.course, self.name, self.init_date, self.end_date)


class AnswerCoEvaluation(models.Model):
    user = models.ForeignKey(UserInCourse, on_delete=models.CASCADE)
    co_evaluation = models.ForeignKey(CoEvaluation, on_delete=models.CASCADE)
    # date = models.DateTimeField(default=datetime.now)

    ANSWERED = "Respondida"
    PENDENT = "Pendiente"

    STATE_TYPE = (
        (PENDENT, "Pendiente"),
        (ANSWERED, "Respondida")
    )

    state = models.CharField(max_length=10, choices=STATE_TYPE)

    def __str__(self):
        return "%s: %s (%s)" % (self.user, self.co_evaluation, self.state)

    @property
    def is_pending(self):
        return self.state == self.PENDENT

    @property
    def is_answered(self):
        return self.state == self.ANSWERED

    @property
    def is_closed(self):
        return not self.co_evaluation.open()

    @property
    def is_open(self):
        return self.co_evaluation.open()

    @property
    def is_published(self):
        return self.co_evaluation.is_published()

    @property
    def status(self):
        if self.is_answered:
            return self.ANSWERED
        elif self.is_closed:
            return CoEvaluation.CLOSED
        elif self.is_pending:
            return self.PENDENT
        elif self.is_open:
            return CoEvaluation.OPEN
        else:
            return CoEvaluation.CLOSED

    def answer(self):
        """
        Ideally here we should define what happens when a student answer a co-evaluation,
        this means, set his state to ANSWERED and per every question in the co-evaluation,
        store the answer in AnswerCoEvaluation.
        When a student answers a CoEvaluation, it give answers with respect to all of his teammates.
        """
        raise NotImplementedError()

    class Meta:
        unique_together = (("user", "co_evaluation"),)


class QuestionsInCoEvaluation(models.Model):
    co_evaluation = models.ForeignKey(CoEvaluation, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)

    def __str__(self):
        return "%s: %s (weight=%s)" % (self.co_evaluation, self.question, self.weight)

    def update_weight(self, weight):
        """
        here we can update the weight of this question in the specific co-evaluation
        """
        raise NotImplementedError()

    class Meta:
        unique_together = (("co_evaluation", "question"),)


class AnswerQuestion(models.Model):
    user_who_answer = models.ForeignKey(User, related_name="answer", on_delete=models.CASCADE)
    user_related = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionsInCoEvaluation, on_delete=models.CASCADE)
    response = models.TextField()

    def __str__(self):
        return "%s response %s related to %s" % (self.user_who_answer,
                                                 self.question, self.user_related)

    @property
    def is_free(self):
        return self.question.is_free()

    @property
    def is_grade(self):
        return self.question.is_grade()

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
