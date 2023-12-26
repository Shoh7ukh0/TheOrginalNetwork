from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views import View
from django.shortcuts import get_object_or_404
from .models import Post, SavedPost, Comment
from .forms import PostForm, CommentForm, SearchForm
from django.contrib.auth.models import User
import redis
from django.conf import settings
from datetime import datetime, timezone
from django.http import JsonResponse
from django.http import HttpResponseServerError
from account.models import Contact, Profile

# соединить с redis
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


class SearchUserView(View):
    template_name = 'base/search.html'

    def get(self, request, *args, **kwargs):
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            users = User.objects.filter(username__icontains=query)
        else:
            users = User.objects.none()

        context = {
            'query': query,
            'users': users,
            'form': form,
        }
        return render(request, self.template_name, context)


class PostListView(View):
    template_name = 'base/index.html'

    def get(self, request, username, tag_slug=None, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        queryset = Profile.objects.filter(user_type=Profile.Status.BLOGER)

        form = PostForm()
        posts = Post.objects.all().order_by('-created_at')
        user_post_count = Post.objects.filter(user=request.user).count()
        users = User.objects.filter(is_active=True)

        user = request.user
        friends = Contact.objects.filter(user_to=user)
        followers = Contact.objects.filter(user_from=user)
        
        for post in posts:
            time_difference = datetime.now(timezone.utc) - post.created_at
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            post.time_since_creation = f"{hours}h {minutes}m ago"

        context = {
            'profile': profile,
            'queryset': queryset,
            'section': 'people', 
            'users': users, 
            'posts': posts, 
            'user_post_count': user_post_count, 
            'form': form, 
            'friends': friends, 
            'followers': followers
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        form = PostForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = self.request.user  # Foydalanuvchi obyektini olib olish
            post.save()
            return redirect('core:post_list', username=user.username)
        return render(request, self.template_name, {'form': form})
    

class EditPostView(View):
    template_name = 'base/edit_post.html'

    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        form = PostForm(instance=post)
        return render(request, self.template_name, {'form': form, 'post': post})

    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.user = self.request.user
            edited_post.save()
            return redirect('core:post_detail', username=user.username, slug=slug)
        return render(request, self.template_name, {'form': form, 'post': post})
    

class PostDetailView(View):
    model = Post
    template_name = 'base/post-details.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        total_views = r.incr(f'Post:{post.id}:views')
        post.save()  # Bu qatorni o'chiring, chunki bu postni saqlash uchun kerak emas

        comments = post.comments.all()
        likes = post.likes.all()
        form = CommentForm()

        # Check if the image attribute has a value
        has_image = post.image.url if post.image else None

        # Check if the video attribute has a value
        has_video = post.video.url if post.video else None

        return render(
            request,
            self.template_name,
            {'post': post, 'comments': comments, 'likes': likes, 'form': form, 'has_image': has_image, 'has_video': has_video, 'total_views': total_views}
        )

    @login_required
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('core:post_detail', username=user.username, slug=post.slug)
        comments = post.comments.all()
        likes = post.likes.all()

        # Check if the image attribute has a value
        has_image = post.image.url if post.image else None

        # Check if the video attribute has a value
        has_video = post.video.url if post.video else None

        return render(
            request,
            self.template_name,
            {'post': post, 'comments': comments, 'likes': likes, 'form': form, 'has_image': has_image, 'has_video': has_video}
        )


class PostCommentView(View):
    template_name = 'base/post-details.html'

    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        form = CommentForm()
        comments = Comment.objects.filter(post=post)
        return render(request, self.template_name, {'post': post, 'form': form, 'comments': comments})

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('core:post_detail', username=user.username, slug=slug)

        comments = Comment.objects.filter(post=post)
        return render(request, self.template_name, {'post': post, 'form': form, 'comments': comments})


class ReplyCommentView(View):
    template_name = 'base/post-details.html'

    def get(self, request, slug, comment_id):
        post = get_object_or_404(Post, slug=slug)
        form = CommentForm()

        comments = Comment.objects.filter(post=post)
        return render(request, self.template_name, {'post': post, 'form': form, 'comments': comments})

    def post(self, request, slug, comment_id):
        post = get_object_or_404(Post, slug=slug)
        form = CommentForm(request.POST)

        if form.is_valid():
            parent_comment = get_object_or_404(Comment, id=comment_id)
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.reply_to = parent_comment
            comment.save()
            return redirect('core:post_detail', username=user.username, slug=slug)

        comments = Comment.objects.filter(post=post)
        return render(request, self.template_name, {'post': post, 'form': form, 'comments': comments})

class LikeCommentView(View):
    def post(self, request, slug, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        if user in comment.likes.all():
            comment.likes.remove(user)
        else:
            comment.likes.add(user)

        return JsonResponse({'likes_count': comment.likes.count()})


class LikePostView(View):
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return redirect('core:post_detail', username=user.username, slug=post.slug)


class DeletePostView(View):
    @method_decorator(login_required)
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug, user=request.user)

        # O'chirilayotgan postga bog'liq Comment obyektlarni o'chirish
        post.comments.all().delete()

        post.delete()
        return redirect('core:post_list', username=user.username)

def hide_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # Check if the user initiating the hide action is the owner of the post
    if request.user == post.user:
        # Toggle the 'hidden' status of the post
        post.hidden = not post.hidden
        post.save()

    # Redirect back to the post detail page or any other page
    return redirect('core:post_list', username=user.username)

class CopyLinkView(View):
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)

        # Assuming you have a function to get the absolute URL of the post
        post_url = post.get_absolute_url()

        # You can also use request.build_absolute_uri(post.get_absolute_url()) if needed

        return JsonResponse({'post_url': post_url})

def share_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    share_url = request.build_absolute_uri(post.get_absolute_url())
    return render(request, 'base/share_post.html', {'share_url': share_url})