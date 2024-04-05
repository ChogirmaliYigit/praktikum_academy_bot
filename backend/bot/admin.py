from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import TelegramUser, Mentor, Course, CourseStudent, SMSVerification


@admin.register(TelegramUser)
class TelegramUserAdmin(ModelAdmin):
    list_display = ("phone_number", "full_name", "telegram_id", "verified",)
    fields = list_display
    search_fields = list_display
    list_filter = ("verified",)
    list_filter_submit = True


@admin.register(Mentor)
class MentorAdmin(ModelAdmin):
    list_display = ("full_name", "description",)
    fields = ("full_name", "image", "description",)
    search_fields = list_display


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ("title", "price", "mentor",)
    fields = ("title", "price", "mentor", "image", "description",)
    list_filter = ("mentor",)
    search_fields = ("title", "price", "mentor", "id", "description")
    list_filter_submit = True


@admin.register(CourseStudent)
class CourseStudentAdmin(ModelAdmin):
    list_display = ("course", "student", "status",)
    fields = list_display
    search_fields = list_display
    list_filter = ("course", "status",)
    list_filter_submit = True


@admin.register(SMSVerification)
class SMSVerificationAdmin(ModelAdmin):
    list_display = ("user", "code", "is_active",)
    fields = list_display
    search_fields = ("user", "code",)
    list_filter = ("is_active",)
    list_filter_submit = True
