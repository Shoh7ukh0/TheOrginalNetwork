from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, CreateView
from django.views import View
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.models import User
import redis
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from accounts.models import Contact
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from .tasks import process_video
from actions.utils import create_action
from django.contrib import messages
from direct.models import Message

# соединить с redis
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


class PostCreateView(LoginRequiredMixin, CreateView):
    login_url = '/accounts/login/'
    template_name = 'base/post-create.html'
    model = Post
    fields = ['caption', 'image', 'video']

    def form_valid(self, form):
        response = super().form_valid(form)
        # Call Celery task to process the post asynchronously
        process_video.delay(self.object.id)
        return response

    def get(self, request, *args, **kwargs):
        # Handle GET request, e.g., when form is submitted with errors
        form = PostForm(data=request.GET)
        return render(request, self.template_name, {'section': 'post', 'form': form})

    def post(self, request, *args, **kwargs):
        # Handle POST request
        form = PostForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            create_action(request.user, 'lifebook post', new_post)
            messages.success(request, 'Post created successfully')
            return redirect('core:post_list')
        return render(request, self.template_name, {'section': 'post', 'form': form})


class PostListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login/'
    template_name = 'base/index-classic.html'
    model = Post
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(hidden=False).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        context['user_post_count'] = Post.objects.filter(user=self.request.user).count()
        context['users'] = User.objects.filter(is_active=True)
        new_post_created = self.request.GET.get('new_post') == 'true'
        context['new_post_created'] = new_post_created

        user = self.request.user
        context['friends'] = Contact.objects.filter(user_to=user)
        context['followers'] = Contact.objects.filter(user_from=user)

        context['current_url'] = self.request.build_absolute_uri()

        context['messages'] = Message.get_messages(user=self.request.user)
        context['active_direct'] = None
        context['directs'] = None

        if context['messages']:
            message = context['messages'][0]
            active_direct = message['user'].username
            directs = Message.objects.filter(user=self.request.user, recipient=message['user'])
            directs.update(is_read=True)
            for message in context['messages']:
                if message['user'].username == active_direct:
                    message['unread'] = 0

        # Vaqt bilan bog'liq ma'lumotlarni olish
        posts = context['posts']
        for post in posts:
            created_at = post.created_at
            now = timezone.now()

            # Vaqt orqali formatlash
            time_difference = now - created_at
            if time_difference.total_seconds() > 3600:  # More than 1 hour ago
                post.created_ago = created_at.strftime(f"%H h ago")
            elif time_difference.total_seconds() > 60:  # 1 to 60 minutes ago
                post.created_ago = f"{int(time_difference.total_seconds() / 60)} m ago"
            elif time_difference.total_seconds() > 1:  # 1 to 59 seconds ago
                post.created_ago = f"{int(time_difference.total_seconds())} s ago"
            else:  # Less than 1 second ago
                post.created_ago = "now"

        return context


    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES, instance=Post(user=request.user))
        if form.is_valid():
            form.save()
            return redirect('core:post_list')
        else:
            print(form.errors)
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
            return redirect('core:post_detail', slug=slug)
        return render(request, self.template_name, {'form': form, 'post': post})
    

class PostDetailView(DetailView):
    model = Post
    template_name = 'base/post-details.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        total_views = r.incr(f'Post:{post.slug}:views')

        comments = post.comments.all()
        likes = post.likes.all()
        form = CommentForm()

        # Check if the image attribute has a value
        has_image = post.image.url if post.image else None

        # Check if the video attribute has a value
        has_video = post.video.url if post.video else None

        context = {
            'post': post, 
            'comments': comments, 
            'likes': likes, 
            'form': form, 
            'has_image': has_image, 
            'has_video': has_video, 
            'total_views': total_views
        }

        return render(request, self.template_name, context)

    @login_required
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('core:post_detail', slug=post.slug)
        comments = post.comments.all()
        likes = post.likes.all()

        # Check if the image attribute has a value
        has_image = post.image.url if post.image else None

        # Check if the video attribute has a value
        has_video = post.video.url if post.video else None

        context = {
            'post': post, 
            'comments': comments, 
            'likes': likes, 
            'form': form, 
            'has_image': has_image, 
            'has_video': has_video,
        }

        return render(request, self.template_name, context)


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
            return redirect('core:post_detail', slug=slug)

        comments = Comment.objects.filter(post=post)
        return render(request, self.template_name, {'post': post, 'form': form, 'comments': comments})



class ReplyCommentView(View):
    template_name = 'base/post-details.html'

    def get(self, request, slug, comment_id):
        post = get_object_or_404(Post, slug=slug)
        form = CommentForm(initial={'parent': comment_id})

        comments = Comment.objects.filter(post=post)

        context = {
            'post': post, 
            'form': form, 
            'comments': comments
        }

        return render(request, self.template_name, context)

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
            return redirect('core:post_detail', slug=slug)

        comments = Comment.objects.filter(post=post)

        context = {
            'post': post, 
            'form': form, 
            'comments': comments
        }

        return render(request, self.template_name, context)

class LikeCommentView(View):
    
    def post(self, request, slug, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        if user in comment.likes.all():
            comment.likes.remove(user)
        else:
            comment.likes.add(user)

        return JsonResponse({'likes_count': comment.likes.count()})


class LikePostView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)

        # Check if the user has already liked the post
        if request.user in post.likes.all():
            # User already liked, remove the like
            post.likes.remove(request.user)
            liked = False
        else:
            # User has not liked, add the like
            post.likes.add(request.user)
            liked = True

        # Return updated like status
        return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})


class DeletePostView(View):
    @method_decorator(login_required)
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug, user=request.user)

        # O'chirilayotgan postga bog'liq Comment obyektlarni o'chirish
        post.comments.all().delete()

        post.delete()
        return redirect('core:post_list')

class HidePostView(View):
    def get(self, request, slug):
        # Retrieve the post using the slug from the URL
        post = get_object_or_404(Post, slug=slug)

        # Check if the user initiating the hide action is the owner of the post
        if request.user.is_authenticated and request.user == post.user:
            # Toggle the 'hidden' status of the post
            post.hidden = not post.hidden
            post.save()

        # Redirect back to the post list page or any other page
        return redirect('core:post_list')

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