from django import forms
from .models import Comment, Post
from django.forms.models import inlineformset_factory

ModuleFormSet = inlineformset_factory(Post, 
                                      fields=['title', 'body'], 
                                      extra=4, 
                                      can_delete=True)

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}))

class SearchForm(forms.Form):
    query = forms.CharField()