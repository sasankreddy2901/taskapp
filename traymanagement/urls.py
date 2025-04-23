from django.urls import path
from . import views


urlpatterns = [
    path('', views.login_redirect_view, name='index'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('agro-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tray/scan/', views.tray_scan, name='tray_scan'),
    path('tray/form/<str:tray_number>/', views.tray_form, name='tray_form'),
    path('api/check-tray/', views.check_tray_exists, name='check_tray_exists'),
    path('agro-admin/create-user/', views.create_user, name='create_user'),
    path('agro-admin/edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('agro-admin/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('agro-admin/user-list/', views.user_list, name='user_list'),
    path('agro-admin/tray-list/', views.tray_data_list, name='tray_data_list'),
    path('api/tray-analytics/<str:tray_number>/', views.tray_analytics, name='tray_analytics'),
]