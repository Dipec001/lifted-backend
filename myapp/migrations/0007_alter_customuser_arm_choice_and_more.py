# Generated by Django 5.0.1 on 2024-02-19 09:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0006_alter_userfollowing_following_user_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="arm_choice",
            field=models.CharField(
                blank=True,
                choices=[
                    ("left_snug", "Left Arm (watch is snug to my wrist)"),
                    ("right_snug", "Right Arm (watch is snug to my wrist)"),
                    ("left_strap", "Left Arm (but I wear wrist straps)"),
                    ("right_strap", "Right Arm (but I wear wrist straps)"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="date_of_birth",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="username",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
