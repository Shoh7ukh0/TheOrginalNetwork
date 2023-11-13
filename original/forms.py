from django import forms
from .models import Post, Comment

class SearchForm(forms.Form):
    q = forms.CharField(label='Search', max_length=100)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'image', 'video']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']