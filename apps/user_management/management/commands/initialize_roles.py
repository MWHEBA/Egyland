from django.core.management.base import BaseCommand
from apps.user_management.models import Role

class Command(BaseCommand):
    help = 'Initialize the three fixed roles: Developer, Admin, and Editor'

    def handle(self, *args, **options):
        # Create Developer role
        developer, created = Role.objects.get_or_create(
            name=Role.DEVELOPER,
            defaults={'description': 'Full access to all system features'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created Developer role'))
        else:
            self.stdout.write(self.style.WARNING(f'Developer role already exists'))

        # Create Admin role
        admin, created = Role.objects.get_or_create(
            name=Role.ADMIN,
            defaults={'description': 'Administrative access with user management'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created Admin role'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin role already exists'))

        # Create Editor role
        editor, created = Role.objects.get_or_create(
            name=Role.EDITOR,
            defaults={'description': 'Content management without user administration'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created Editor role'))
        else:
            self.stdout.write(self.style.WARNING(f'Editor role already exists'))

        self.stdout.write(self.style.SUCCESS('Roles initialization completed!')) 