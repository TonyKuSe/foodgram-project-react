from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import models
# from django.db.transaction import atomic
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
import base64

from django.core.files.base import ContentFile
from reviews.models import Ingredient, Recipe, Tag, RecipeIngredient, Favorites, Carts
# from users.models import Subscriptions, FoodUser
# from rest_framework.validators import UniqueTogetherValidator
# from rest_framework.decorators import api_view
from users.serializers import UserSerializer


User = get_user_model()

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class ShortRecipeSerializer(ModelSerializer):
    """Сериализатор для показа модели Recipe."""
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("__all__",)


class TagSerializer(ModelSerializer):
    """Сериализатор для вывода тэгов."""
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ("__all__",)

    def validate(self, data: OrderedDict) -> OrderedDict:
        """Унификация вводных данных при создании/редактировании тэга."""
        for attr, value in data.items():
            data[attr] = value.sttrip(" ").upper()
        return data


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ("__all__",)


class CreateRecipeIngredientSerializer(ModelSerializer):

    id = serializers.IntegerField()
    class Meta: 
        model = RecipeIngredient
        fields = ('id', 'amount')
        read_only_fields = ('id',)


class FiedIngredientsList(serializers.Field):
    
    def to_representation(self, value):
        recipe_id = value.core_filters
        ingredient = Ingredient.objects.all().filter(recipe=recipe_id ['recipe__id']).values(
             "id", "name", "measurement_unit", 'rec_ingredient__amount')
        ingredients = []
        for i in ingredient:
            ingredients.append({
                'id': i['id'],
                'name': i['name'],
                'measurement_unit': i['measurement_unit'],
                'amount': i['rec_ingredient__amount']
            })
        return ingredients
    def to_internal_value(self, data):
        return data


class RecipeSerializer(ModelSerializer):
    """Сериализатор для рецептов."""
    
    author = UserSerializer(many=False, required=False)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = FiedIngredientsList()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(
        required=False, allow_null=True
    )
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            "is_favorite",
            "is_shopping_cart",
        )

    def get_is_favorited(self, recipe):
        return self.context['request'].user.favorites.filter(recipe=recipe).exists() 
        
    def get_is_in_shopping_cart(self, recipe):  
        return Carts.objects.all().filter(user=self.context['request'].user, recipe=recipe).exists()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(Ingredient,id=ingredient['id'])
            RecipeIngredient.objects.create(
                recipe_id=recipe.id,
                ingredient_id=current_ingredient.id,
                amount=ingredient['amount'])
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        x = list
        RecipeIngredient.objects.all().filter(recipe_id=instance.id).delete()
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe_id=instance.id,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'])
        tags_data = self.initial_data.pop('tags')
        instance.tags.set(tags_data)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.save()
        return instance


class RecipeSerializerList(ModelSerializer):
    """Сериализатор для рецептов."""
    author = UserSerializer(many=False)
    tags = TagSerializer(many=True)
    ingredients = FiedIngredientsList()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, recipe):
        return Favorites.objects.all().filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        return Carts.objects.all().filter(recipe=recipe).exists()


class FavoritRecipeSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False,)
    name = serializers.CharField(required=False)
    image = Base64ImageField(
        required=False, allow_null=True
    )
    cooking_time = serializers.IntegerField(required=False)
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
 
    def create(self, validated_data):
        user = validated_data.pop('user')
        recipe =  validated_data.pop('recipe')
        Favorites.objects.create(
                recipe=recipe,
                user=user)
        return recipe


class CartsRecipeSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    image = Base64ImageField(
        required=False, allow_null=True
    )
    cooking_time = serializers.IntegerField(required=False)
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def create(self, validated_data):
        user = validated_data.pop('user')
        recipe =  validated_data.pop('recipe')
        Carts.objects.get_or_create(
                recipe=recipe,
                user=user)
        return recipe
