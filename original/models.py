from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
    

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)
    hashtag = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.user.username} - {self.caption[:20]}'

        

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey('Post', on_delete=models.PROTECT, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text