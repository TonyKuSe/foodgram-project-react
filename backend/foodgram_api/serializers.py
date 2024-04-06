import base64
from collections import OrderedDict
from django.shortcuts import get_object_or_404

from django.db.models import F
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from reviews.models import (Ingredient, Recipe,
                            Tag, RecipeIngredient,
                            Favorites, Carts)
from reviews.enums import Limits
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
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class TagSerializer(ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')

    def validate(self, data: OrderedDict) -> OrderedDict:
        """Унификация вводных данных при создании/редактировании тэга."""
        for attr, value in data.items():
            data[attr] = value.sttrip(' ').upper()
        return data


class IngredientSerializer(ModelSerializer):
    """Сериализатор для ингридиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')

# class FiedIngredientsList(serializers.Field): 

 

#     def to_representation(self, value): 

#         recipe_id = value.core_filters 

#         ingredient = Ingredient.objects.all().filter( 

#             recipe=recipe_id['recipe__id']).values( 

#                 'id', 'name', 'measurement_unit', 'rec_ingredient__amount') 

#         ingredients = [] 

#         for i in ingredient: 

#             ingredients.append({ 

#                 'id': i['id'], 

#                 'name': i['name'], 

#                 'measurement_unit': i['measurement_unit'], 

#                 'amount': i['rec_ingredient__amount'] 

#             }) 

#         return ingredients 

 

    # def to_internal_value(self, data): 

    #     return data 

class RecipeSerializer(ModelSerializer):
    """Сериализатор для рецептов."""

    author = UserSerializer(many=False, required=False)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = SerializerMethodField()
    # ingredients = FiedIngredientsList() 
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(
        required=False, allow_null=True
    )
    cooking_time = serializers.IntegerField(
        min_value=Limits.MIN_COOKING_TIME,
        max_value=Limits.MAX_COOKING_TIME
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
            'is_favorite',
            'is_shopping_cart',
        )

    def get_ingredients(self, recipe):
        return Ingredient.objects.all().filter(
            recipe=recipe.id).values(
            'id', 'name', 'measurement_unit',
            amount=F('rec_ingredient__amount')
        )

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.all().exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.carts.all().exists()

    # def create_ingredients(self, recipe, ingredients,):
    #     recipe_ingredients = []
    #     for ingredient in ingredients:
    #         amount = ingredient['amount']
    #         if (
    #             amount < Limits.MIN_AMOUNT_INGREDIENTS
    #             or amount > Limits.MAX_AMOUNT_INGREDIENTS
    #         ):
    #             raise ValueError(
    #                 f'Значение amount должно быть от '
    #                 f'{Limits.MIN_AMOUNT_INGREDIENTS} до '
    #                 f'{Limits.MAX_AMOUNT_INGREDIENTS}.'
    #             )
    #         recipe_ingredient = RecipeIngredient(
    #             recipe=recipe,
    #             ingredient_id=ingredient['id'],
    #             amount=amount
    #         )
    #         recipe_ingredients.append(recipe_ingredient)
    #     RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients = self.initial_data.pop('ingredients')
        tags = self.initial_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        # self.create_ingredients(recipe, ingredients)
        for ingredient in ingredients: 

            current_ingredient = get_object_or_404( 

                Ingredient, id=ingredient['id'] 

            ) 

            RecipeIngredient.objects.create( 

                recipe_id=recipe.id, 

                ingredient_id=current_ingredient.id, 

                amount=ingredient['amount']) 
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = self.initial_data.pop('ingredients')
        instance.rec_ingredient.all().delete()
        self.create_ingredients(instance, ingredients_data)
        tags_data = self.initial_data.pop('tags')
        instance.tags.set(tags_data)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        return instance


class RecipeSerializerList(ModelSerializer):
    """Сериализатор для выведения всех рецептов."""

    author = UserSerializer(many=False)
    tags = TagSerializer(many=True)
    ingredients = SerializerMethodField()
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

    def get_ingredients(self, recipe):
        return Ingredient.objects.all().filter(
                recipe=recipe.id).values(
                    'id', 'name', 'measurement_unit',
                    amount=F('rec_ingredient__amount')
                )

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.all().exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.carts.all().exists()


class FavoritRecipeSerializer(ModelSerializer):
    """Сериализатор для избраного."""
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
        recipe = validated_data.pop('recipe')
        Favorites.objects.create(
            recipe=recipe,
            user=user
        )
        return recipe


class CartsRecipeSerializer(ModelSerializer):
    """Сериализатор для работы корзины."""
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
        recipe = validated_data.pop('recipe')
        Carts.objects.get_or_create(
            recipe=recipe,
            user=user
        )
        return recipe
