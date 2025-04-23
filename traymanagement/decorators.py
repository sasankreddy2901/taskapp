from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import UserProfile

def admin_required(view_func):
    """Decorator to check if user is an admin."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            if request.user.profile.user_type == 'admin':
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('user_dashboard')
        except UserProfile.DoesNotExist:
            # Create a default profile if it doesn't exist
            UserProfile.objects.create(user=request.user, user_type='user')
            messages.error(request, "You don't have permission to access this page.")
            return redirect('user_dashboard')
    
    return _wrapped_view