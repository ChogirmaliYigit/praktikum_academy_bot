from django.db import models


class TelegramUser(models.Model):
    full_name = models.CharField(max_length=500, null=True, blank=True)
    telegram_id = models.BigIntegerField(unique=True)
    phone_number = models.CharField(max_length=30, unique=True)
    verified = models.BooleanField(default=False)

    def __str__(self): return self.full_name or f"User ({self.id})"

    class Meta:
        db_table = "telegram_users"


class Mentor(models.Model):
    full_name = models.CharField(max_length=500)
    image = models.ImageField(upload_to="mentors/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self): return self.full_name

    class Meta:
        db_table = "mentors"


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    image = models.ImageField(upload_to="course_images/", null=True, blank=True)
    mentor = models.ForeignKey(Mentor, on_delete=models.PROTECT)

    def __str__(self): return self.title

    class Meta:
        db_table = "courses"


class CourseStudent(models.Model):
    REQUESTED = "requested"
    CANCELED = "canceled"
    ACCEPTED = "accepted"
    STUDYING = "studying"

    STATUSES = (
        (REQUESTED, "Requested"),
        (CANCELED, "Canceled"),
        (ACCEPTED, "Accepted"),
        (STUDYING, "Studying"),
    )

    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    student = models.ForeignKey(TelegramUser, on_delete=models.PROTECT)
    status = models.CharField(max_length=30, choices=STATUSES, default=REQUESTED)

    def __str__(self): return f"{self.course.title} da {self.student.full_name}"

    class Meta:
        db_table = "course_students"


class SMSVerification(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "sms_verifications"


class Chat(models.Model):
    chat_id = models.BigIntegerField(unique=True)

    def __str__(self): return str(self.chat_id)

    class Meta:
        db_table = "chats"
