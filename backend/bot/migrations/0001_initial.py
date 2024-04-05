# Generated by Django 5.0.3 on 2024-04-04 15:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Mentor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("full_name", models.CharField(max_length=500)),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="mentors/"),
                ),
                ("description", models.TextField(blank=True, null=True)),
            ],
            options={
                "db_table": "mentors",
            },
        ),
        migrations.CreateModel(
            name="TelegramUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("full_name", models.CharField(blank=True, max_length=500, null=True)),
                ("telegram_id", models.BigIntegerField(unique=True)),
                ("phone_number", models.CharField(max_length=30, unique=True)),
            ],
            options={
                "db_table": "telegram_users",
            },
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=20)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="course_images/"
                    ),
                ),
                (
                    "mentor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="bot.mentor"
                    ),
                ),
            ],
            options={
                "db_table": "courses",
            },
        ),
        migrations.CreateModel(
            name="CourseStudent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("requested", "Requested"),
                            ("canceled", "Canceled"),
                            ("accepted", "Accepted"),
                            ("studying", "Studying"),
                        ],
                        default="requested",
                        max_length=30,
                    ),
                ),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="bot.course"
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="bot.telegramuser",
                    ),
                ),
            ],
            options={
                "db_table": "course_students",
            },
        ),
    ]
