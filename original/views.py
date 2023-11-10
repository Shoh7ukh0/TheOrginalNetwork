from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import EmailPostForm, CommentForm, SearchForm, PostForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity

# Create your views here.

@login_required
def home(request):
    posts = Post.objects.all()
    return render(request, 'base.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'base/index.html', {'form': form})

def post_detail(request):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED)
    
    # Ushbu post uchun faol sharhlar ro'yxati
    comments = post.comments.filter(active=True)
    # Foydalanuvchi sharhlar shakli
    form = CommentForm()

    # Список схожих постов
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
                                        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                                        .order_by('-same_tags','-publish')[:4]

    
    return render(request,'base/post-details.html', {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts})

# Elektiron pochtaga Xabar yuborish
def post_share(request, post_id):
    # Identifikatori bo'yicha postni oling
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        # Shakl qayta ishlash uchun yuborildi
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Shakl maydonlari muvaffaqiyatli tasdiqlandi
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'your_account@gmail.com', [cd['to']])

            sent = True
        # ... elektron pochta xabarini yuboring
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

@require_POST
def post_comment(request):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED)
    comment = None
    # Izoh e'lon qilindi
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Ma'lumotlar bazasida saqlamasdan Comment sinfi ob'ektini yarating
        comment = form.save(commit=False)
        # Fikr bildirish uchun post tayinlang
        comment.post = post
        # Fikrni ma'lumotlar bazasiga saqlang
        comment.save()

    return render(request, 'base/index.html', {'post': post, 'form': form, 'comment': comment})

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
                ).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request, 'blog/post/search.html',
                {'form': form, 
                'query': query,
                'results': results})