from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm, SubscriptionForm
from .models import Profile
from original.models import Post
from actions.utils import create_action
from actions.models import Action
from .models import Contact, Subscription
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages

class ProfileView(View):
    template_name = 'account/dashboard.html'

    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        posts = Post.objects.filter(user=user)
        followers = Subscription.objects.filter(subscribed_to=user).count()
        following = Subscription.objects.filter(subscriber=user).count()
        is_following = Subscription.objects.filter(subscriber=request.user, subscribed_to=user).exists()
        subscription_form = SubscriptionForm(initial={'subscriber': request.user, 'subscribed_to': user})

        one_day_ago = timezone.now() - timedelta(days=1)
        new_users = User.objects.filter(date_joined__gte=one_day_ago)

        # Obuna bo'lgan foydalanuvchilar sonini qo'shing
        subscribers_count = Subscription.objects.filter(subscribed_to=user).count()

        context = {
            'profile': profile,
            'posts': posts,
            'followers': followers,
            'following': following,
            'is_following': is_following,
            'subscription_form': subscription_form,
            'new_users': new_users,
            'subscribers_count': subscribers_count,  # Obuna bo'lgan foydalanuvchilar soni
        }
        return render(request, self.template_name, context)


@login_required
def toggle_subscription(request, username):
    subscribed_to_user = get_object_or_404(User, username=username)

    try:
        subscription = Subscription.objects.get(subscriber=request.user, subscribed_to=subscribed_to_user)
        subscription.delete()  # Obunani o'chirish
    except Subscription.DoesNotExist:
        Subscription.objects.create(subscriber=request.user, subscribed_to=subscribed_to_user)  # Obuna bo'lish

    return redirect('profile', username=username)


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

@method_decorator(require_POST, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UserFollowView(View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('id')
        action = request.POST.get('action')
        
        if user_id and action:
            try:
                user = User.objects.get(id=user_id)
                if action == 'follow':
                    Contact.objects.get_or_create(user_from=request.user, user_to=user)
                    create_action(request.user, 'is following', user)
                else:
                    Contact.objects.filter(user_from=request.user, user_to=user).delete()
                return JsonResponse({'status': 'ok'})
            except User.DoesNotExist:
                return JsonResponse({'status': 'error'})
        
        return JsonResponse({'status': 'error'})

