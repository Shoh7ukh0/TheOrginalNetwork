from django.contrib.auth.models import User
from django.forms.widgets import ClearableFileInput
from .models import Profile
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',
                                                                'placeholder': 'Foydalanuvchi nomini kiriting'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control fakepassword',
                                                                'placeholder': 'Parolni kiriting'}))

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class':'form-control',
                                                                'placeholder': 'Yangi parolni kiriting'}))
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput(attrs={'class':'form-control fakepassword',
                                                                'placeholder': 'Parolni tasdiqlang'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']

        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Yangi foydalanuvchi nomini kiriting'
                }),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ismni kiriting'
                }),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Elektron pochtani kiriting'
                }
            )
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
    
    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.exclude(id=self.instance.id).filter(email=data)

        if qs.exists():
            raise forms.ValidationError(' Email already in use.')
        return data
    
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                }
            )
        }
        
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'bio', 'photo', 'user_type', 'location']

        widgets = {
            'date_of_birth': forms.TextInput(
                attrs={
                    'class': 'form-control flatpickr',
                    'value': '12/12/1990'
                }),

            'bio': forms.Textarea(
                attrs={
                    'class': 'form-control', 
                    'rows': 3,
                    'placeholder': "Description (Required)"
                }),

            'photo': ClearableFileInput(
                attrs={
                    'class': 'dropzone dropzone-default card shadow-none',
                }),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Toshkent'
                }),
        }