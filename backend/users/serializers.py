from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import models
from django.db.transaction import atomic
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers

from reviews.models import Ingredient, Recipe, Tag
from users.models import Subscriptions, FoodUser
# from reviews.validators import ingredients_validator, tags_exist_validator
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.decorators import api_view
from djoser.serializers import SetPasswordSerializer


User = get_user_model()

class UserSetPasswordSerializer(SetPasswordSerializer):
    

    class Meta:
        model = User
        fields = ( 
           'id',
        )

class UserRetrieveSerializer(ModelSerializer):
    
    email = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


    def get_email(self, obj):
        x = get_object_or_404(User, id=self.context['request'].data['id'])
        return x.email

    def get_username(self, obj):
        x = get_object_or_404(User, id=self.context['request'].data['id'])
        return x.username

    def get_first_name(self, obj):
        x = get_object_or_404(User, id=self.context['request'].data['id'])
        return x.first_name

    def get_last_name(self, obj):
        x = get_object_or_404(User, id=self.context['request'].data['id'])
        return x.last_name

    def get_id(self, obj):
        x = get_object_or_404(User, id=self.context['request'].data['id'])
        return x.id
    
    def get_is_subscribed(self, obj: User):

        user = self.context.get('request').user.id
        # if user.is_anonymous or (user == obj):
        #     return False
        # x = user.publisher.filter(author=obj).exists()
        return user

class UserSerializer(ModelSerializer):
    
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed', 'count')

    def get_is_subscribed(self, obj):

        # user = self.context.get('request').user
        # if user.is_anonymous == True:
        #     return False
        # elif user == obj:
        #     return False
        # return user.publisher.filter(author=obj).exists()
        return False

    def create(self, validated_data: dict) -> User:
        """Создаёт нового пользователя с запрошенными полями."""
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class FollowSerializer(ModelSerializer):

    email = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = Subscriptions
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            'is_subscribed',
        )
        read_only_fields = [

            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):
        # if user.is_anonymous or (user == x):
        #     return False
        return Subscriptions.objects.filter(
            author=self.context['request'].data['id'],
            user=self.context.get('request').user.id).exists()
    
    def get_email(self, obj):
        
        return self.context['request'].user.email
    
    def get_username(self, obj):
        
        return self.context['request'].user.username
    
    def get_first_name(self, obj):
        
        return self.context['request'].user.first_name
        
    def get_last_name(self, obj):
        
        return self.context['request'].user.last_name
    
    def get_id(self, obj):
        
        return self.context['request'].user.id


    def create(self, validated_data):
        subscriptions = Subscriptions.objects.create(
            author=get_object_or_404(User, id=self.context['request'].data['id']),
            user=self.context['request'].user,
        )
        subscriptions.save()
        return subscriptions
    

    def validate_following(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError('Нельзя подписаться на самого себя')
        return value


class UserSubscribeSerializer(UserSerializer):
    
    id = serializers.IntegerField(
        source='author.id')
    email = serializers.EmailField(
        source='author.email')
    username = serializers.CharField(
        source='author.username')
    first_name = serializers.CharField(
        source='author.first_name')
    last_name = serializers.CharField(
        source='author.last_name')
    
    # recipes = ShortRecipeSerializer(many=True, read_only=True)
    
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            # # 'recipes',
            # 'recipes_count',
        )
        read_only_fields = ('__all__',)

    def get_is_subscribed(*args):
        """Проверка подписки пользователей."""
        return True


