from django import forms
from .models import Post, Comment
from django.forms.widgets import ClearableFileInput

class SearchForm(forms.Form):
    q = forms.CharField(label='Search', max_length=100)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'hashtag', 'image', 'video']
    
        widgets = {
            'caption': forms.TextInput(
                attrs={
                    'class': 'form-control pe-4 fs-3 lh-1 border-0',
                    'placeholder': 'Add a Post...'
                }),
            'hashtag': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Add a hashtag...'
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
                    'placeholder': 'Add a Comment...'
                }),
        }