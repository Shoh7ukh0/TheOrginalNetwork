# yourapp/tasks.py
from celery import shared_task
from .models import Post

@shared_task
def process_post(slug):
    try:
        post = Post.objects.get(slug=slug)
        # Perform the processing tasks on the post
        # e.g., send emails, update database, etc.
        print(f"Processing post: {post.caption}")
    except Post.DoesNotExist:
        print(f"Post with id {slug} does not exist")
