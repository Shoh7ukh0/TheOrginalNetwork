from django.contrib.auth.models import User
from .models import Profile
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',
                                                                'placeholder': 'Enter the username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control fakepassword',
                                                                'placeholder': 'Enter the password'}))

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class':'form-control',
                                                                'placeholder': 'Enter the username'}))
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput(attrs={'class':'form-control fakepassword',
                                                                'placeholder': 'Enter the password'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']

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
    
    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.exclude(id=self.instance.id)\
                         .filter(email=data)
        if qs.exists():
            raise forms.ValidationError('Email already in use.')
        return data
        
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']