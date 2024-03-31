from django.contrib import admin

from .models import (Favorites, Ingredient, Recipe, RecipeIngredient, Carts, Tag)
from users.models import (Subscriptions) 

EMPTY_MSG = '-пусто-'

class RecipeIngredientAdmin(admin.StackedInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id','name',
        'author', 'text',
        'cooking_time', 
        # 'get_favorite_count'
        'tags', 'ingredients',
        'pub_date',)
    search_fields = (
        'name', 'cooking_time',
        'author__email', 'ingredients__name')
    list_filter = ('pub_date', 'tags',)
    inlines = (RecipeIngredientAdmin,)
    empty_value_display = EMPTY_MSG

    @admin.display(description='Тэги')
    def tags(self, obj):
        return obj.tags.all()

    @admin.display(description=' Ингредиенты ')
    def ingredients(self, obj):
        return obj.ingredients.name

    # @admin.display(description='В избранном')
    # def get_favorite_count(self, obj):
    #     return obj.favorite_recipe.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    empty_value_display = EMPTY_MSG


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit',)
    search_fields = (
        'name', 'measurement_unit',)
    empty_value_display = EMPTY_MSG


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'author', 'date_added',)
    search_fields = (
        'user__email', 'author__email',)
    empty_value_display = EMPTY_MSG


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'get_recipe', 'get_count')
    empty_value_display = EMPTY_MSG

    @admin.display(
        description='Рецепты')
    def get_recipe(self, obj):
        return [
            f'{item["name"]} ' for item in obj.recipe.name]

    @admin.display(
        description='В избранных')
    def get_count(self, obj):
        return obj.recipe.count()


@admin.register(Carts)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'get_recipe', 'get_count')
    empty_value_display = EMPTY_MSG

    @admin.display(description='Рецепты')
    def get_recipe(self, obj):
        if isinstance(obj.recipe, list):
            return [
                f'{item["name"]} ' for item in obj.recipe if 'name' in item
            ]
        return 'Некорректный формат рецепта'

    @admin.display(description='В избранных')
    def get_count(self, obj):
        return obj.recipe.all().count()
