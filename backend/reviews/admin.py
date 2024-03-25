from django.contrib import admin

from .models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                     Carts, Tag)

admin.site.register(Favorites)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(Carts)
admin.site.register(Tag)


