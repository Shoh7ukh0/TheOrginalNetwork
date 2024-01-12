from rest_framework import serializers, viewsets
from django.contrib.auth.models import User

from .models import Notification, Profile, Contact

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = 'is_locked', 'user', 'email', 'date_of_birth', 'bio', 'photo', 'bg_photo', 'following', 'disable_chat', 'user_type', 'saved_posts', 'location', 'created_at'


class ProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'photo', 'bg_photo', 'user_type', 'location']

    def update(self, instance, validated_data):
        # Ma'lumotlarni yangilash
        instance.bio = validated_data.get('bio', instance.bio)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.bg_photo = validated_data.get('bg_photo', instance.bg_photo)
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # Parolni shifrlash
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Foydalanuvchi profilini yaratish
        Profile.objects.create(user=user)

        return user


class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = 'user_from', 'user_to', 'created'


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']


class UserConnectionsSerializer(serializers.Serializer):
    friends = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    def get_friends(self, obj):
        # Friends haqida ma'lumot olish
        friends = Contact.objects.filter(user_from=obj['user'])
        return FriendSerializer(friends, many=True).data

    def get_followers(self, obj):
        # Followers haqida ma'lumot olish
        followers = Contact.objects.filter(user_to=obj['user'])
        return FollowerSerializer(followers, many=True).data

    def get_profile(self, obj):
        # Profil ma'lumotlarini olish
        return ProfileSerializer(obj['profile']).data


class ProfileToPDFSerializer(serializers.Serializer):
    user_profile = serializers.SerializerMethodField()

    def get_user_profile(self, obj):
        user_profile = obj.user.profile
        # Yoki siz o'zingizga kerakli ma'lumotlarni qo'shing

        return user_profile