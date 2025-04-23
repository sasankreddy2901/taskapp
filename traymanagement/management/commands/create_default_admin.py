import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from traymanagement.models import UserProfile

class Command(BaseCommand):
    help = 'Creates default admin user if no users exist'

    def handle(self, *args, **options):
        if User.objects.count() == 0:
            admin = User.objects.create_superuser(
                username='anjireddy',
                email='anjireddy@kapilagro.com',
                password='anji@kapil123',
                first_name='Anji',
                last_name='Reddy'
            )
            
            # Ensure profile is created
            try:
                profile = admin.profile
                profile.user_type = 'admin'
                profile.save()
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=admin, user_type='admin')
                
            self.stdout.write(self.style.SUCCESS('Default admin user created!'))
            self.stdout.write(self.style.WARNING('Username: anjireddy'))
            self.stdout.write(self.style.WARNING('Password: anji@kapil123'))
            self.stdout.write(self.style.WARNING('Please change these credentials immediately after first login!'))
        else:
            self.stdout.write(self.style.WARNING('Admin users already exist, skipping creation.'))