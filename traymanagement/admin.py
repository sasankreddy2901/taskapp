from django.contrib import admin
from .models import TrayData, UserProfile

@admin.register(TrayData)
class TrayDataAdmin(admin.ModelAdmin):
    list_display = ('tray_number', 'user', 'sowing_date', 'first_cutting_date', 'second_cutting_date', 'third_cutting_date')
    list_filter = ('sowing_date', 'user')
    search_fields = ('tray_number', 'observations', 'user__username')
    date_hierarchy = 'sowing_date'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'created_by', 'phone')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'user__email', 'phone')