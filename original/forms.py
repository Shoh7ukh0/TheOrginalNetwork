from django import forms
from .models import Post, Comment
from django.forms.widgets import ClearableFileInput

class SearchForm(forms.Form):
    q = forms.CharField(label='Qidirmoq', max_length=100)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'hashtags', 'image', 'video', 'location']
    
        widgets = {
            'caption': forms.TextInput(
                attrs={
                    'class': 'form-control pe-4 border-0',
                    'rows': 2,
                    'placeholder': 'Postizga sarlavha yozing...'
                }),
            'hashtags': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': "Hashtag qo'shing..."
                }),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': "Locatsiya qo'shing..."
                }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

        widgets = {
            'text': forms.TextInput(
                attrs={
                    'class': 'form-control pe-5 bg-light',
                    'rows': 1,
                    'placeholder': "Fikr qo'shish..."
                }),
        }