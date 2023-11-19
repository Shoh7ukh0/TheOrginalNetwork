from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import get_object_or_404
from .models import Post
from .forms import PostForm, CommentForm, SearchForm
from django.contrib.auth.models import User

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

    def get(self, request, tag_slug=None, *args, **kwargs):
        posts = Post.objects.all().order_by('-id')
        return render(request, self.template_name, {'posts': posts})


class CreatePostView(View):
    template_name = 'base/create_post.html'

    def get(self, request, *args, **kwargs):
        form = PostForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = self.request.user  # Foydalanuvchi obyektini olib olish
            post.save()
            return redirect('core:post_list')
        return render(request, self.template_name, {'form': form})
    

class EditPostView(View):
    template_name = 'base/edit_post.html'

    def get(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)
        form = PostForm(instance=post)
        return render(request, self.template_name, {'form': form, 'post': post})

    def post(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.user = self.request.user
            edited_post.save()
            return redirect('core:post_detail', post_id=post.id)
        return render(request, self.template_name, {'form': form, 'post': post})
    

class PostDetailView(View):
    template_name = 'base/post-details.html'

    def get(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)
        # post.save()  # Bu qatorni o'chiring, chunki bu postni saqlash uchun kerak emas

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
            {'post': post, 'comments': comments, 'likes': likes, 'form': form, 'has_image': has_image, 'has_video': has_video}
        )

    @login_required
    def post(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('core:post_detail', post_id=post.id)
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

class AddCommentView(View):
    template_name = 'base/post-details.html'

    def post(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = self.request.user  # Foydalanuvchi obyektini olib olish
            comment.post = post
            comment.save()
            return redirect('core:post_detail', post_id=post.id)
        return render(request, self.template_name, {'post': post, 'form': form})



class LikePostView(View):
    def post(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return redirect('core:post_detail', post_id=post_id)


class DeletePostView(View):
    @login_required
    def get(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id, user=request.user)
        post.delete()
        return redirect('core:post_list')