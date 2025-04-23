from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created if one doesn't exist."""
    if created:
        # Check if the user is a superuser (admin)
        user_type = 'admin' if instance.is_superuser else 'user'
        UserProfile.objects.create(user=instance, user_type=user_type)