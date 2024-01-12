from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Notification, Profile, Contact
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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from .serializers import ProfileSerializer, NotificationSerializer, ProfileEditSerializer, \
    UserRegistrationSerializer, UserFollowSerializer, UserListSerializer, UserDetailSerializer, \
    UserConnectionsSerializer, ProfileToPDFSerializer

from original.serializers import SavedPostSerializer
from actions.serializers import ActionSerializer


class SearchUserAPIView(APIView):
    def get(self, request, *args, **kwargs):
        form = SearchForm(request.GET)
        queryset = Profile.objects.filter(user_type=Profile.Status.BLOGER)

        if form.is_valid():
            query = form.cleaned_data.get('q', '')
            users = User.objects.filter(username__icontains=query)
        else:
            query = ''
            users = User.objects.none()

        data = {
            'query': query,
            'users': [
                {'username': user.username, 'email': user.email} for user in users
            ],
            'form': form,
            'queryset': queryset,
        }

        return Response(data, status=status.HTTP_200_OK)


class ProfileAPIView(APIView):
    @method_decorator(login_required)
    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        posts = Post.objects.filter(user=user)
        queryset = Profile.objects.filter(user_type=Profile.Status.BLOGER)
        one_day_ago = timezone.now() - timedelta(days=1)
        new_users = User.objects.filter(date_joined__gte=one_day_ago)
        notifications = Notification.objects.filter(user=user)

        serializer = ProfileSerializer(profile)

        data = {
            'profile': serializer.data,
            'posts': posts,
            'queryset': queryset,
            'new_users': new_users,
            'notifications': notifications,
        }

        return Response(data, status=status.HTTP_200_OK)

        @method_decorator(login_required)
        def post(self, request, username, *args, **kwargs):
            user = get_object_or_404(User, username=username)
            profile = get_object_or_404(Profile, user=user)
            form = ProfileEditForm(request.POST, request.FILES, instance=profile)

            if 'lock_profile' in request.POST:
                profile.is_locked = not profile.is_locked
                profile.save()
                messages.success(request, 'Profil muvaffaqiyatli lock/unlock qilindi.')
                return Response({'detail': 'Profil muvaffaqiyatli lock/unlock qilindi.'}, status=status.HTTP_200_OK)

            if form.is_valid():
                form.save()
                messages.success(request, 'Profil ma\'lumotlari saqlandi.')
            else:
                messages.error(request, 'Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.')

            message = request.POST.get('message')
            sender = request.user
            notifications(sender, message)
            messages.success(request, 'Xabarlar yuborildi.')

            serializer = ProfileSerializer(profile)

            data = {
                'profile': serializer.data,
                'message': 'Profil ma\'lumotlari saqlandi.',
            }

            return Response(data, status=status.HTTP_200_OK)

class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.data)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return Response({'detail': 'Logged in successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Disabled account'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Invalid form data'}, status=status.HTTP_400_BAD_REQUEST)

class DashboardAPIView(APIView):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        actions = Action.objects.exclude(user=request.user)
        following_ids = request.user.following.values_list('id', flat=True)

        if following_ids:
            actions = actions.filter(user_id__in=following_ids)
        
        actions = actions.select_related('user', 'user__profile').prefetch.related('target')[:10]

        serializer = ActionSerializer(actions, many=True)

        data = {
            'section': 'dashboard',
            'actions': serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)

class RegistrationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(request.data)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()

            Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')

            serializer = UserRegistrationSerializer(new_user)

            data = {
                'new_user': serializer.data,
                'detail': 'User registered successfully',
            }

            return Response(data, status=status.HTTP_201_CREATED)

        errors = {'detail': 'Invalid registration data'}
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class EditProfileAPIView(APIView):

    @staticmethod
    def add_notification(request, user, message):
        Notification.objects.create(user=user, message=message)
        messages.success(request, 'Notification added.')

    def get(self, request, *args, **kwargs):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        data = {'user_form': user_form, 'profile_form': profile_form}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user_form = UserEditForm(instance=request.user, data=request.data)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.data, files=request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            # Qo'shilgan xabarni yuborish
            self.add_notification(request, request.user, 'Profil ma\'lumotlari o\'zgartirildi.')
            
            data = {'detail': 'Profile updated successfully'}
            return Response(data, status=status.HTTP_200_OK)
        else:
            errors = {'detail': 'Error updating your profile'}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

class UserListAPIView(APIView):
    @authentication_classes([])
    @permission_classes([])
    def get(self, request, *args, **kwargs):
        users = User.objects.filter(is_active=True)
        data = [{'id': user.id, 'username': user.username} for user in users]
        return Response(data, status=status.HTTP_200_OK)

class UserDetailAPIView(APIView):
    @authentication_classes([])
    @permission_classes([])
    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username, is_active=True)
        data = {'id': user.id, 'username': user.username, 'email': user.email, 'other_fields': '...'}
        return Response(data, status=status.HTTP_200_OK)


class UserFollowAPIView(APIView):
    @authentication_classes([IsAuthenticated])
    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('id')
        action = request.data.get('action')

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

                return Response({'status': 'ok'}, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({'status': 'error'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        

class MyProfileAboutAPIView(APIView):
    @authentication_classes([IsAuthenticated])
    @permission_classes([IsAuthenticated])
    def get(self, request, *args, **kwargs):
        # Foydalanuvchini profilini olish
        profile = Profile.objects.get(user=request.user)

        # Profil ma'lumotlarini JSON formatida qaytarish
        data = {'profile': {'bio': profile.bio, 'photo': profile.photo.url, 'other_fields': '...'}}
        return Response(data, status=status.HTTP_200_OK)


class MyProfileConnectionsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            friends = Contact.objects.filter(user_to=user)
            followers = Contact.objects.filter(user_from=user)

            # Profil ma'lumotlarini JSON formatida qaytarish
            serializer = UserConnectionsSerializer({
                'friends': friends,
                'followers': followers,
                'profile': user.profile,
            })

            return Response(serializer.data)

        except Exception as e:
            return Response({'error': f"Error in my_profile_connections view: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SavedPostsView(APIView):
    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        saved_posts = user_profile.saved_posts.all()

        # Saqlangan postlar haqida ma'lumotlarni JSON formatida qaytarish
        serializer = SavedPostSerializer(saved_posts, many=True)
        return Response(serializer.data)


class SavePostView(APIView):
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        user_profile = request.user.profile

        # Check if the post is already saved
        if not user_profile.saved_posts.filter(slug=slug).exists():
            user_profile.saved_posts.add(post)

            # Saqlangan post haqida ma'lumotlarni JSON formatida qaytarish
            serializer = SavedPostSerializer(user_profile.saved_posts.all(), many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Post has already been saved.'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteSavedPostView(APIView):
    def delete(self, request, username, slug, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        user_profile = request.user.profile
        post = get_object_or_404(Post, slug=slug)

        # Check if the post is saved by the user
        if user_profile.saved_posts.filter(slug=slug).exists():
            # Unsave the post
            user_profile.saved_posts.remove(post)

            # Saqlangan postlardan keyingi ma'lumotlarni JSON formatida qaytarish
            serializer = SavedPostSerializer(user_profile.saved_posts.all(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Post is not saved by the user.'}, status=status.HTTP_400_BAD_REQUEST)


class HelpView(APIView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('account/help.html')
        return Response({'html_content': template.render()}, status=status.HTTP_200_OK)

class HelpDetailsView(APIView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('account/help-details.html')
        return Response({'html_content': template.render()}, status=status.HTTP_200_OK)

class PrivacyView(APIView):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('account/privacy-and-terms.html')
        return Response({'html_content': template.render()}, status=status.HTTP_200_OK)

class ProfileToPDFView(APIView):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        # Foydalanuvchi profilini olish
        user_profile = request.user

        # Shablonni yuklash
        template = loader.get_template('account/profile_pdf_template.html')

        # Shablon bilan ma'lumotlarni to'ldirish
        serializer = ProfileToPDFSerializer({'user_profile': user_profile})
        context = {'user_profile': serializer.data}

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

        # PDF-ni Response orqali foydalanuvchiga yuborish
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_profile.pdf"'

        return response


class NotificationsAPIView(APIView):
    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        notifications = Notification.objects.filter(user=user)

        user_1 = request.user
        if request.GET.get('id'):
            user2_id = request.GET.get('id')
            user_2 = get_object_or_404(User, id=user2_id)
            get_create = ChatSession.create_if_not_exists(user_1, user_2)
            if get_create:
                messages.add_message(request, messages.SUCCESS, f'{user_2.username} successfully added in your chat list!!')
            else:
                messages.add_message(request, messages.SUCCESS, f'{user_2.username} already added in your chat list!!')
            
            # Xabar yuborish
            self.send_notification(request.user, user_2, message)

            return HttpResponseRedirect('/notifications', username=username)
        else:
            user_all_friends = ChatSession.objects.filter(Q(user1=user_1) | Q(user2=user_1))
            user_list = []
            for ch_session in user_all_friends:
                user_list.append(ch_session.user1.id)
                user_list.append(ch_session.user2.id)
            all_user = User.objects.exclude(Q(username=user_1.username) | Q(id__in=list(set(user_list))))

        serializer = NotificationSerializer(notifications, many=True)

        context = {
            'notifications': serializer.data,
            'all_user': all_user,
        }

        return Response(context)

    def send_notification(self, sender, receiver, message):
        Notification.objects.create(user=receiver, message=message)

        
# def notifications(sender, message):
#     users = User.objects.exclude(username=sender.username)
#     for user in users:
#         Notification.objects.create(user=user, message=message)