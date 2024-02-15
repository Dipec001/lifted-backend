# Generated by Django 5.0.1 on 2024-02-14 17:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0004_set"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="bio",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="profile_photo",
            field=models.ImageField(blank=True, null=True, upload_to="profile_photos/"),
        ),
        migrations.CreateModel(
            name="UserFollowing",
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
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "following_user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="follower",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="following",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
            },
        ),
        migrations.AddConstraint(
            model_name="userfollowing",
            constraint=models.UniqueConstraint(
                fields=("user_id", "following_user_id"), name="unique_followers"
            ),
        ),
    ]