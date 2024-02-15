from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import models
from django.db.transaction import atomic
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from reviews import svc
from reviews.models import Ingredient, Recipe, Tag, RecipeIngredient
from users.models import Subscriptions, FoodUser
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.decorators import api_view
from users.serializers import UserSerializer


User = get_user_model()


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
    """Сериализатор для вывода ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', "measurement_unit")
        read_only_fields = ("id", 'name', "measurement_unit",)

        
    
class RecipeSerializer(ModelSerializer):
    """Сериализатор для рецептов."""

    ingredients = IngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    #image = svc.Base64ImageField(required=False, allow_null=True)
    
    # is_favorited = SerializerMethodField()
    # is_in_shopping_cart = SerializerMethodField()
    

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            # 'image',
            'name',
            'text',
            'cooking_time',
        )
        # read_only_fields = (
        #     "is_favorite",
        #     "is_shopping_cart",
        # )

    def validate(self, data: OrderedDict) -> OrderedDict:
        """Проверка вводных данных при создании/редактировании рецепта."""
        tags_ids: list[int] = self.initial_data.get("tags")
        ingredients = self.initial_data.get("ingredients")

        if not tags_ids or not ingredients:
            raise ValidationError("Недостаточно данных.")

        tags = tags_ids, Tag
        ingredients = ingredients, Ingredient

        data.update(
            {
                "tags": tags,
                "ingredients": ingredients,
                "author": self.context.get("request").user,
            }
        )
        return data
    
    def create(self, validated_data):
        # initial_data = self.initial_data
        ing = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        # ingredients = initial_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags) 
        for ingredient in ing: 
            current_ingredient = Ingredient.objects.get(ingredient)
            RecipeIngredient.objects.create(
                recipe_id=recipe.id,
                ingredient_id=current_ingredient,
                amount=ingredient)
        return recipe

