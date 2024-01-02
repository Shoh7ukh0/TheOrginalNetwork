from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.utils.text import slugify
from django.urls import reverse

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    caption = models.TextField()
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)
    hashtags = models.CharField(max_length=500)
    duration = models.DurationField(null=True, blank=True)
    hidden = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.caption[:20]}'

    def save(self, *args, **kwargs):
        # Auto-generate the slug when saving the post
        if not self.slug:
            self.slug = slugify(self.caption)  # Use the post title to generate a slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:post_detail', args=[str(self.slug)])
        

class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey('Post', on_delete=models.PROTECT, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.text}'

    def get_reply_comments(self):
        return Comment.objects.filter(reply_to=self)