from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from actions.utils import create_action
from actions.models import Action
from .models import Contact
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'account/dashboard.html'

    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        posts = Post.objects.filter(user=user)

        # Qachon ro'yxatdan o'tganligi 24 soat ichida bo'lgan foydalanuvchilarni topamiz
        one_day_ago = timezone.now() - timedelta(days=1)
        new_users = User.objects.filter(date_joined__gte=one_day_ago)

        context = {
            'profile': profile,
            'posts': posts,
            'new_users': new_users,
        }
        return render(request, self.template_name, context)

    def post(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profil ma\'lumotlari saqlandi.')
        else:
            messages.error(request, 'Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.') 

        return redirect('account:dashboard', username=username)

class LoginView(View):
    template_name = 'account/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('account:dashboard')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticate successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
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

class RegisterView(View):
    template_name = 'account/register.html'

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
            return render(request, 'account/register_done.html', {'new_user': new_user})
        return render(request, self.template_name, {'user_form': user_form})

class EditProfileView(View):
    template_name = 'account/edit.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})

class UserListView(View):
    template_name = 'account/dashboard.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        users = User.objects.filter(is_active=True)
        return render(request, self.template_name, {'section': 'people', 'users': users})

class UserDetailView(View):
    template_name = 'account/dashboard.html'

    @method_decorator(login_required)
    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username, is_active=True)
        return render(request, self.template_name, {'section': 'people', 'user': user})

class UserFollowView(View):
    @method_decorator(require_POST)
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('id')
        action = request.POST.get('action')
        if user_id and action:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})

