from django.contrib import admin
from .models import Post, Comment, HashTag

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['caption', 'created_at']
    filter_horizontal = ('hashtags',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'reply_to']

admin.site.register(HashTag)