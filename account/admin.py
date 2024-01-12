from django.contrib import admin
from .models import Profile, Contact

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'photo', 'bg_photo', 'location', 'created_at', ]
    raw_id_fields = ['user', 'saved_posts']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['user_from', 'user_to']