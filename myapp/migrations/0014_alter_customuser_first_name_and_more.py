# Generated by Django 5.0.1 on 2024-02-20 11:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0013_alter_workoutsession_group"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="first_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="last_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
