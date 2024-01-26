# tasks.py
import os
from celery import shared_task
from moviepy.editor import VideoFileClip
from PIL import Image
from django.core.files import File
from .models import Post

@shared_task
def process_video(slug):
    post = Post.objects.get(slug=slug)
    video_path = post.video.path

    # Extract images
    clip = VideoFileClip(video_path)
    frames = clip.iter_frames(fps=1)  # Extract a frame per second

    for i, frame in enumerate(frames):
        # Save each frame as an image
        image = Image.fromarray(frame)
        image_path = f"media/post_images/{slug}/frame_{i}.jpg"
        image.save(image_path)

        # Create a new PostImage object and associate it with the post
        post_image = post.images.create(image=File(open(image_path, 'rb')))
        os.remove(image_path)  # Remove the temporary image file

    # Determine video duration and update the post
    post.duration = clip.duration
    post.save()
