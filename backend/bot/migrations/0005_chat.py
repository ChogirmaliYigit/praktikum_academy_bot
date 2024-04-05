# Generated by Django 5.0.3 on 2024-04-05 05:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0004_telegramuser_verified"),
    ]

    operations = [
        migrations.CreateModel(
            name="Chat",
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
                ("chat_id", models.BigIntegerField(unique=True)),
            ],
            options={
                "db_table": "chats",
            },
        ),
    ]