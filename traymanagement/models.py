from django.db import models
from django.contrib.auth.models import User

class TrayData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tray_entries")
    tray_number = models.CharField(max_length=50, unique=True)
    sowing_date = models.DateField()
    
    first_cutting_date = models.DateField(null=True, blank=True)
    second_cutting_date = models.DateField(null=True, blank=True)
    third_cutting_date = models.DateField(null=True, blank=True)
    
    yield_1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Yield in kg")
    yield_2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Yield in kg")
    yield_3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Yield in kg")
    
    observations = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Tray {self.tray_number} - {self.sowing_date}"
    
    class Meta:
        verbose_name = "Tray Data"
        verbose_name_plural = "Tray Data"
        ordering = ['-updated_at']

class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'Regular User'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_users")
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"