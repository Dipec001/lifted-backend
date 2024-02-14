# myapp/management/commands/populate_data.py

from django.core.management.base import BaseCommand
from myapp.populate import create_workout_types_and_exercises

class Command(BaseCommand):
    help = 'Populate workout types and exercises data'

    def handle(self, *args, **options):
        create_workout_types_and_exercises()
        self.stdout.write(self.style.SUCCESS('Successfully populated workout types and exercises.'))
