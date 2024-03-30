from collections import OrderedDict

from django.contrib.auth import get_user_model

from django.shortcuts import get_object_or_404

from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers

from reviews.models import Recipe
from users.models import Subscriptions
# from rest_framework.validators import UniqueTogetherValidator

from djoser.serializers import SetPasswordSerializer


User = get_user_model()

class UserSetPasswordSerializer(SetPasswordSerializer):
    """Сериализатор для смены пароля"""
    new_password = serializers.CharField()
    current_password =  serializers.CharField()
    class Meta:
        model = User
        fields = ( 
           'new_password',
           'current_password'
        )

class UserRetrieveSerializer(ModelSerializer):
    """Сериализатор для выыедения запрошенного пользователя"""
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
        return obj.email

    def get_username(self, obj):
        return obj.username

    def get_first_name(self, obj):
        return obj.first_name

    def get_last_name(self, obj):
        return obj.last_name

    def get_id(self, obj):
        return obj.id
    
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.follower.filter(author=obj.id).exists()

class UserMeSerializer(ModelSerializer):
    """Сериализатор для для выведения информации о текущем пользавтеле"""
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
        return obj.email

    def get_username(self, obj):
        return obj.username

    def get_first_name(self, obj):
        return obj.first_name

    def get_last_name(self, obj):
        return obj.last_name

    def get_id(self, obj):
        return obj.id
    
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.follower.filter(author=obj.id).exists()

class UserSerializer(ModelSerializer):
    """Сериализатор для создания пользователя"""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('id',)

    def create(self, validated_data):
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

class RecipeForFollowSerializer(ModelSerializer):
    """Сериализатор для выведения рецептов в подписках""" 
    class Meta:
        model = Recipe
        fields =(
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]

class FollowSerializer(ModelSerializer):
    """"""
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            'is_subscribed',
            'recipes',
            'recipes_count',
            
        )
        read_only_fields = [

            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей."""
        return Subscriptions.objects.filter(
            author=obj.id,
            user=self.context.get('request').user.id).exists()

    def get_recipes_count(self, obg):
        """Количество рецептов у автора"""
        return Recipe.objects.all().filter(author=obg.id).count()
    
    def get_recipes(self, obg):
        """Массив объектов Recipe автора"""
        recipes = Recipe.objects.all().filter(author=obg.id)
        limit = self.context.get('request')._request.GET.get('recipes_limit')
        serializer = RecipeForFollowSerializer(
            data=recipes[:limit],
            many=True
        )
        serializer.is_valid()
        return serializer.data

    def validate(self, data):
        """Проверка подписок пользователя и автора."""
        user = self.context.get('request').user
        author = self.initial_data.get('author')
        
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if Subscriptions.objects.filter(
            user=user, author=author
        ).exists():
            raise serializers.ValidationError(
                f'Вы уже подписаны на {author.username}.'
            )
        return data
    
    def create(self, validated_data):
        """Создание подписок пользователя и автора"""
        author = validated_data.pop('author')
        user = self.context.get('request').user
        subscriptions = Subscriptions.objects.create(
            author=author,
            user=user,
        )
        subscriptions.save()
        return author


class ListUserSubscribeSerializer(UserSerializer):
    """Сериализатор для выведения подписок"""
    email = serializers.EmailField(
        source='author.email')
    id = serializers.IntegerField(
        source='author.id')
    username = serializers.CharField(
        source='author.username')
    first_name = serializers.CharField(
        source='author.first_name')
    last_name = serializers.CharField(
        source='author.last_name')
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('__all__',)

    def get_recipes_count(self, obg):
        """Количество рецептов у автора"""
        return Recipe.objects.all().filter(author=obg.id).count()
    
    def get_recipes(self, obg):
        """Массив объектов Recipe автора"""
        recipes = Recipe.objects.all().filter(author=obg.id)
        limit = self.context.get('request')._request.GET.get('recipes_limit')
        serializer = RecipeForFollowSerializer(
            data=recipes[:int(limit)],
            many=True
        )
        serializer.is_valid()
        return serializer.data
    
    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей."""
        return Subscriptions.objects.filter(
            author=obj.id,
            user=self.context.get('request').user.id).exists()
