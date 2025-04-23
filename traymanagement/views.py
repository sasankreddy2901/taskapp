from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q

from .models import TrayData, UserProfile
from .forms import TrayDataForm, UserRegistrationForm
from .decorators import admin_required

def login_redirect_view(request):
    """Redirect users based on their user type after login."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        profile = request.user.profile
        if profile.user_type == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('user_dashboard')
    except UserProfile.DoesNotExist:
        # If no profile exists, create a default one
        UserProfile.objects.create(user=request.user, user_type='user')
        return redirect('user_dashboard')

@login_required
def user_dashboard(request):
    """Dashboard for regular users."""
    tray_data_list = TrayData.objects.filter(user=request.user)
    paginator = Paginator(tray_data_list, 10)  # Show 10 entries per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    all_trays = TrayData.objects.all().values_list('tray_number', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'all_trays': all_trays, 
    }
    return render(request, 'traymanagement/user_dashboard.html', context)

# Update the admin_dashboard view to include all trays

@login_required
@admin_required
def admin_dashboard(request):
    """Dashboard for admin users."""
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
     
    # Filter tray data
    if search_query:
        tray_data_list = TrayData.objects.filter(
            Q(tray_number__icontains=search_query) | 
            Q(user__username__icontains=search_query) |
            Q(observations__icontains=search_query)
        )
    else:
        tray_data_list = TrayData.objects.all()
    
    # Get all trays for the analytics dropdown
    all_trays = TrayData.objects.all().values_list('tray_number', flat=True).distinct()
    
    # Paginate results
    paginator = Paginator(tray_data_list, 15)  # Show 15 entries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get user statistics
    total_users = User.objects.count()
    admin_users = UserProfile.objects.filter(user_type='admin').count()
    regular_users = UserProfile.objects.filter(user_type='user').count()
    # Cutting stats
    first_cutting_count = TrayData.objects.filter(first_cutting_date__isnull=False).count()
    second_cutting_count = TrayData.objects.filter(second_cutting_date__isnull=False).count()
    third_cutting_count = TrayData.objects.filter(third_cutting_date__isnull=False).count()
    
    if request.method == "POST" and "delete_tray_id" in request.POST:
        tray_id = request.POST.get("delete_tray_id")
        TrayData.objects.filter(id=tray_id).delete()
        messages.success(request, "Tray data deleted successfully.")
        return redirect("admin_dashboard")
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_users': total_users,
        'admin_users': admin_users,
        'regular_users': regular_users,
        'total_trays': TrayData.objects.count(),
        'all_trays': all_trays,  # Add this to the context
        "first_cutting_count": first_cutting_count,
        "second_cutting_count": second_cutting_count,
        "third_cutting_count": third_cutting_count,
    }
    return render(request, 'traymanagement/admin_dashboard.html', context)

@login_required
def tray_scan(request):
    """Page for scanning QR codes and filling tray data."""
    return render(request, 'traymanagement/tray_scan.html')

@login_required
def tray_form(request, tray_number=None):
    """Form for adding or editing tray data."""
    instance = None
    
    # Check if the tray entry already exists
    if tray_number:
        instance = TrayData.objects.filter(tray_number=tray_number).first()
        
    

    
    # Remove the permission check to allow any user to edit any tray
    # The commented code below shows what was previously restricting access
    # if instance and instance.user != request.user and not request.user.profile.user_type == 'admin':
    #     messages.error(request, "You don't have permission to edit this tray data.")
    #     return redirect('user_dashboard')
    
    # Handle form submission
    if request.method == 'POST':
        form = TrayDataForm(request.POST, instance=instance)
        if form.is_valid():
            tray_data = form.save(commit=False)
            if not instance:  # New record
                tray_data.user = request.user
                tray_data.tray_number = tray_number
            tray_data.save()
            
            messages.success(request, f"Tray data for {tray_number} has been saved successfully.")
            if request.user.profile.user_type == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
    else:
        # Initialize form with instance or tray_number
        if instance:
            form = TrayDataForm(instance=instance)
        else:
            form = TrayDataForm(initial={'tray_number': tray_number})
    
    context = {
        'form': form,
        'tray_number': tray_number,
        'is_edit': instance is not None,
    }
    return render(request, 'traymanagement/tray_form.html', context)


@login_required
def check_tray_exists(request):
    """API endpoint to check if a tray number exists."""
    tray_number = request.GET.get('tray_number', '')
    if not tray_number:
        return JsonResponse({'error': 'No tray number provided'}, status=400)
    
    # Check if tray exists
    tray_exists = TrayData.objects.filter(tray_number=tray_number).exists()
    
    return JsonResponse({
        'exists': tray_exists,
        'tray_number': tray_number,
        'form_url': reverse('tray_form', args=[tray_number])
    })

@login_required
@admin_required
def create_user(request):
    """Form for admin to create new users."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True, created_by=request.user)
            messages.success(request, f"User {user.username} has been created successfully.")
            return redirect('admin_dashboard')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'traymanagement/create_user.html', context)

@login_required
@admin_required
def user_list(request):
    """List of all users for admin."""
    search_query = request.GET.get('search', '')
    
    if search_query:
        users = User.objects.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    else:
        users = User.objects.all()
    
    paginator = Paginator(users, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'traymanagement/user_list.html', context)

@login_required
def tray_data_list(request):
    """List all tray data for admin with sorting capability."""
    search_query = request.GET.get('search', '')
    sort_field = request.GET.get('sort', 'tray_number')
    sort_order = request.GET.get('order', 'desc')  # Default order is descending
    
    # Validate sort field to prevent injection
    allowed_sort_fields = [
        'tray_number', 'user__username', 'sowing_date', 
        'yield_1', 'yield_2', 'yield_3', 'created_at', 'updated_at'
    ]
    
    if sort_field not in allowed_sort_fields:
        sort_field = 'tray_number'  # Default if invalid
    
    # Filter tray data
    if search_query:
        tray_data_list = TrayData.objects.filter(
            Q(tray_number__icontains=search_query) | 
            Q(observations__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    else:
        tray_data_list = TrayData.objects.all()
    
    # Handle standard fields (not tray_number) with normal ordering
    if sort_field != 'tray_number':
        if sort_order == 'desc':
            tray_data_list = tray_data_list.order_by(f'-{sort_field}')
        else:
            tray_data_list = tray_data_list.order_by(sort_field)
    else:
        # For tray_number, we need to use Python sorting
        # Convert queryset to list for Python sorting
        tray_data_list = list(tray_data_list)
        
        # Define a key function to extract number from tray_number
        def extract_number(obj):
            try:
                # Try to extract just the number part
                tray_str = obj.tray_number
                # Extract digits from the string
                import re
                num_str = re.sub(r'\D', '', tray_str)
                return int(num_str) if num_str else 0
            except (ValueError, AttributeError):
                return 0
        
        # Sort the list
        tray_data_list.sort(key=extract_number, reverse=(sort_order == 'desc'))
    
    paginator = Paginator(tray_data_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_sort': sort_field,
        'current_order': sort_order,
    }
    return render(request, 'traymanagement/tray_list.html', context)


@login_required
@admin_required
def edit_user(request, user_id):
    """Edit an existing user."""
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Get the current password to determine if it should be changed
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        # Create a copy of POST data to modify
        post_data = request.POST.copy()
        
        # If password fields are empty, remove them from the form data
        # This will prevent the form from validating/changing passwords
        if not password1 and not password2:
            post_data.pop('password1', None)
            post_data.pop('password2', None)
        
        form = UserRegistrationForm(post_data, instance=user_obj)
        
        if form.is_valid():
            try:
                user = form.save(commit=True, created_by=request.user)
                messages.success(request, f"User {user.username} has been updated successfully.")
                return redirect('user_list')
            except Exception as e:
                messages.error(request, f"Error updating user: {str(e)}")
    else:
        # Pre-populate the form with existing user data
        try:
            initial_data = {
                'user_type': user_obj.profile.user_type,
                'phone': user_obj.profile.phone,
            }
            form = UserRegistrationForm(instance=user_obj, initial=initial_data)
            
            # Remove the password field requirement for existing users
            form.fields['password1'].required = False
            form.fields['password2'].required = False
            form.fields['password1'].help_text = "Leave empty to keep current password"
            form.fields['password2'].help_text = "Leave empty to keep current password"
            
        except Exception as e:
            messages.error(request, f"Error loading user data: {str(e)}")
            form = UserRegistrationForm(instance=user_obj)
    
    context = {
        'form': form,
        'editing': True,
        'user_obj': user_obj
    }
    return render(request, 'traymanagement/edit_user.html', context)

@login_required
@admin_required
def delete_user(request, user_id):
    """Delete a user."""
    user_obj = get_object_or_404(User, id=user_id)
    
    # Prevent deleting yourself
    if user_obj == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('user_list')
    
    try:
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f"User {username} has been deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting user: {str(e)}")
    
    return redirect('user_list')

@login_required
def tray_analytics(request, tray_number):
    """Get tray analytics data in JSON format."""
    try:
        # Debug output
        print(f"Analytics request for tray: {tray_number}")
        
        # Try to find the tray data
        try:
            tray_data = TrayData.objects.get(tray_number=tray_number)
        except TrayData.DoesNotExist:
            # If not found, try to clean the tray number format
            # Sometimes browsers might encode "Tray Number: X" in the URL
            if "Tray Number:" in tray_number:
                # Try to extract just the number
                clean_number = tray_number.split(":")[-1].strip()
                tray_data = TrayData.objects.get(tray_number__icontains=clean_number)
            else:
                # If still not found, raise the original exception
                raise
        
        # Prepare data for charts
        yield_data = []
        
        if tray_data.first_cutting_date and tray_data.yield_1:
            yield_data.append({
                'date': tray_data.first_cutting_date.strftime('%Y-%m-%d'),
                'cutting': '1st Cutting',
                'yield': float(tray_data.yield_1)
            })
            
        if tray_data.second_cutting_date and tray_data.yield_2:
            yield_data.append({
                'date': tray_data.second_cutting_date.strftime('%Y-%m-%d'),
                'cutting': '2nd Cutting',
                'yield': float(tray_data.yield_2)
            })
            
        if tray_data.third_cutting_date and tray_data.yield_3:
            yield_data.append({
                'date': tray_data.third_cutting_date.strftime('%Y-%m-%d'),
                'cutting': '3rd Cutting',
                'yield': float(tray_data.yield_3)
            })
        
        # Debug output
        print(f"Found {len(yield_data)} data points for tray {tray_number}")
        
        return JsonResponse({'success': True, 'data': yield_data})
    except TrayData.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Tray not found'})
    except Exception as e:
        print(f"Error in tray analytics: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})