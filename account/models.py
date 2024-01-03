import datetime
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from original.models import Post


class ActiveUser(models.Model):
    username = models.CharField(max_length=125)
    is_admin = models.BooleanField(default=False)

class Profile(models.Model):
    class Status(models.TextChoices):
        BLOGER = 'Bloger'
        SOFTWARE_ENGINEERING = 'Software engineering'
        GRAPHIC_DESIGNER = 'Graphic designer'
        FOOTBALL_PLAYER = 'Football player'
        MUSICIAN = 'Musician'
        SMM_MANAGER = 'SMM manager'
        MARKETOLOGY = 'Marketology'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField()
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    following = models.ManyToManyField('self', through='Contact', related_name='followers', symmetrical=False, blank=True)
    disable_chat = models.BooleanField(default=False)
    user_type = models.CharField(max_length=100, choices=Status.choices, default=Status.BLOGER)
    saved_posts = models.ManyToManyField(Post, related_name='saved_by', blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Profile of {self.user.username}'
    
class Contact(models.Model):
    user_from = models.ForeignKey(User,
                                  related_name='rel_from_set',
                                  on_delete=models.PROTECT)
    user_to = models.ForeignKey(User,
                                related_name='rel_to_set',
                                on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
        ]
        ordering = ['-created']

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


# Add following field to User dynamically
user_model = get_user_model()
user_model.add_to_class('following',
                        models.ManyToManyField('self',
                            through=Contact,
                            related_name='followers',
                            symmetrical=False))