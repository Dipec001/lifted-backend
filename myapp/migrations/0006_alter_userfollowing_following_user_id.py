# Generated by Django 5.0.1 on 2024-02-14 19:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0005_customuser_bio_customuser_profile_photo_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userfollowing",
            name="following_user_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="followers",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
