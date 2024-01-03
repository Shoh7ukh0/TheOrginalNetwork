from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact
from original.models import Post
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from actions.utils import create_action
from actions.models import Action
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.http import HttpResponseServerError
from django.db.models import Q
from core.models import ChatSession, ChatMessage
from original.forms import SearchForm
import pdfkit
from django.template import loader


class SearchUserView(View):
    template_name = 'account/search.html'

    def get(self, request, *args, **kwargs):
        form = SearchForm(request.GET)
        queryset = Profile.objects.filter(user_type=Profile.Status.BLOGER)
        
        if form.is_valid():
            query = form.cleaned_data.get('q', '')
            users = User.objects.filter(username__icontains=query)
        else:
            query = ''
            users = User.objects.none()

        context = {
            'query': query,
            'users': users,
            'form': form,
            'queryset':queryset,
        }
        
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'account/dashboard.html'

    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        posts = Post.objects.filter(user=user)
        queryset = Profile.objects.filter(user_type=Profile.Status.BLOGER)
        one_day_ago = timezone.now() - timedelta(days=1)
        new_users = User.objects.filter(date_joined__gte=one_day_ago)

        context = {
            'profile': profile,
            'posts': posts,
            'queryset': queryset,
            'new_users': new_users,
        }
        return render(request, self.template_name, context)

    def post(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)

        # Lock/unlock so'rovi qabul qilinganmi tekshirish
        if 'lock_profile' in request.POST:
            profile.is_locked = not profile.is_locked
            profile.save()
            messages.success(request, 'Profil muvaffaqiyatli lock/unlock qilindi.')
            return redirect('dashboard', username=username)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profil ma\'lumotlari saqlandi.')
        else:
            messages.error(request, 'Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.')

        return redirect('dashboard', username=username)

class LoginView(View):
    template_name = 'registration/login.html'  # Ma'lumotnoma HTML fayli

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('core:post_list')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse("Hali Ro'yxatdan o'tmagansiz!")
        else:
            form = LoginForm()

        return render(request, self.template_name, {'form': form})

class DashboardView(View):
    template_name = 'account/dashboard.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        actions = Action.objects.exclude(user=request.user)
        following_ids = request.user.following.values_list('id', flat=True)
        
        if following_ids:
            actions = actions.filter(user_id__in=following_ids)
        actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]
        return render(request, self.template_name, {'section': 'dashboard', 'actions': actions})

class RegistrationView(View):
    template_name = 'account/register.html'
    success_template_name = 'account/register_done.html'

    def get(self, request, *args, **kwargs):
        user_form = UserRegistrationForm()
        return render(request, self.template_name, {'user_form': user_form})

    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')

            return render(request, self.success_template_name, {'new_user': new_user})

        return render(request, self.template_name, {'user_form': user_form})

class EditProfileView(View):
    template_name = 'account/edit.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})

    @method_decorator(login_required)
    def post(self, request, username, *args, **kwargs):
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('my_profile_about')
        else:
            messages.error(request, 'Error updating your profile')
        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})

class UserListView(View):
    template_name = 'account/user/list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        users = User.objects.filter(is_active=True)
        return render(request, self.template_name, {'section': 'people', 'users': users})

class UserDetailView(View):
    template_name = 'account/user/detail.html'

    @method_decorator(login_required)
    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username, is_active=True)
        return render(request, self.template_name, {'section': 'people', 'user': user})


@method_decorator(login_required, name='dispatch')
class UserFollowView(View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('id')
        action = request.POST.get('action')

        if user_id and action:
            try:
                user = get_object_or_404(User, id=user_id)
                if action == 'follow':
                    Contact.objects.get_or_create(
                        user_from=request.user,
                        user_to=user
                    )
                else:
                    Contact.objects.filter(
                        user_from=request.user,
                        user_to=user
                    ).delete()

                return JsonResponse({'status': 'ok'})

            except User.DoesNotExist:
                return JsonResponse({'status': 'error'})

        return JsonResponse({'status': 'error'})
        

def my_profile_about(request):
    # Foydalanuvchini profilini olish
    profile = Profile.objects.get(user=request.user)

    # Profil ma'lumotlarini shablonga o'tkazish
    context = {
        'profile': profile,
    }

    return render(request, 'account/my-profile-about.html', context)


def my_profile_connections(request):
    try:
        user = request.user
        friends = Contact.objects.filter(user_to=user)
        followers = Contact.objects.filter(user_from=user)

        context = {
            'friends': friends,
            'followers': followers,
        }

        return render(request, 'account/my-profile-connections.html', context)
    except Exception as e:
        return HttpResponseServerError(f"Error in my_profile_connections view: {e}")

def saved_posts(request):
    user_profile = request.user.profile
    saved_posts = user_profile.saved_posts.all()

    return render(request, 'account/save_post.html', {'saved_posts': saved_posts})

def save_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    user_profile = request.user.profile

    # Check if the post is already saved
    if not user_profile.saved_posts.filter(slug=slug).exists():
        user_profile.saved_posts.add(post)

    saved_posts = user_profile.saved_posts.all()

    return render(request, 'account/save_post.html', {'saved_posts': saved_posts})

def delete_saved_post(request, username, slug):
    user = get_object_or_404(User, username=username)
    user_profile = request.user.profile
    post = get_object_or_404(Post, slug=slug)

    # Check if the post is saved by the user
    if user_profile.saved_posts.filter(slug=slug).exists():
        # Unsave the post
        user_profile.saved_posts.remove(post)

    return redirect('core:post_list')


def help(request):
    return render(request, 'account/help.html')

def help_details(request):
    return render(request, 'account/help-details.html')

def privacy(request):
    return render(request, 'account/privacy-and-terms.html')

@login_required
def notifications(request):
    user_1 = request.user
    if request.GET.get('id'):
        user2_id = request.GET.get('id')
        user_2 = get_object_or_404(User,id = user2_id)
        get_create = ChatSession.create_if_not_exists(user_1,user_2)
        if get_create:
            messages.add_message(request,messages.SUCCESS,f'{user_2.username} successfully added in your chat list!!')
        else:
            messages.add_message(request,messages.SUCCESS,f'{user_2.username} already added in your chat list!!')
        return HttpResponseRedirect('/notifications')
    else:
        user_all_friends = ChatSession.objects.filter(Q(user1 = user_1) | Q(user2 = user_1))
        user_list = []
        for ch_session in user_all_friends:
            user_list.append(ch_session.user1.id)
            user_list.append(ch_session.user2.id)
        all_user = User.objects.exclude(Q(username=user_1.username)|Q(id__in = list(set(user_list))))
    return render(request, 'account/notifications.html',{'all_user' : all_user})

class ProfileToPDFView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        # Foydalanuvchi profilini olish
        user_profile = request.user.profile

        # Shablonni yuklash
        template = loader.get_template('account/profile_pdf_template.html')

        # Shablon bilan ma'lumotlarni to'ldirish
        context = {
            'user_profile': user_profile,
        }

        # HTML-ni generatsiya qilish
        html_content = template.render(context)

        # HTML-ni PDF-ga o'girish
        pdf_options = {
            'page-size': 'A4',
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
        }

        pdf_file = pdfkit.from_string(html_content, False, options=pdf_options)

        # PDF-ni HttpResponse orqali foydalanuvchiga yuborish
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_profile.pdf"'

        return response