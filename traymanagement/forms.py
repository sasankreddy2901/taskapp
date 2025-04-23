from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import TrayData, UserProfile

class TrayDataForm(forms.ModelForm):
    class Meta:
        model = TrayData
        fields = ['tray_number', 'sowing_date', 'first_cutting_date', 'second_cutting_date', 
                  'third_cutting_date', 'yield_1', 'yield_2', 'yield_3', 'observations']
        widgets = {
            'tray_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'sowing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'first_cutting_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'second_cutting_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'third_cutting_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'yield_1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Yield in kg'}),
            'yield_2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Yield in kg'}),
            'yield_3': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Yield in kg'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class UserRegistrationForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'Regular User'),
    )
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

        # If this is an existing user (editing), make passwords optional
        if self.instance and self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        
        # When editing a user (instance has pk) and no password provided
        if self.instance and self.instance.pk:
            password1 = cleaned_data.get('password1', '')
            password2 = cleaned_data.get('password2', '')
            
            # If one password field is provided but not the other
            if bool(password1) != bool(password2):
                raise forms.ValidationError("Both password fields must be filled out or both left empty.")
                
            # If both are empty, remove validation errors related to passwords
            if not password1 and not password2:
                if 'password1' in self._errors:
                    del self._errors['password1']
                if 'password2' in self._errors:
                    del self._errors['password2']
        
        return cleaned_data
    def clean_username(self):
         username = self.cleaned_data.get('username')
         if self.instance and self.instance.pk:
        # If this is an existing user, allow them to keep the same username
             if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This username is already taken.")
         else:
        # For new users, check if username exists as usual
             if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
         return username
        
    def save(self, commit=True, created_by=None):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Handle password only when creating a new user or explicitly changing it
        if not self.instance.pk or (self.cleaned_data.get('password1') and self.cleaned_data.get('password2')):
            user.set_password(self.cleaned_data["password1"])
            
        if commit:
            user.save()
            
            # Check if profile already exists
            try:
                # If profile exists, update it
                profile = user.profile
                profile.user_type = self.cleaned_data['user_type']
                profile.phone = self.cleaned_data['phone']
                if created_by:
                    profile.created_by = created_by
                profile.save()
            except UserProfile.DoesNotExist:
                # Create a new profile only if it doesn't exist
                UserProfile.objects.create(
                    user=user,
                    user_type=self.cleaned_data['user_type'],
                    phone=self.cleaned_data['phone'],
                    created_by=created_by
                )
        
        return user