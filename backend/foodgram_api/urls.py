from django.urls import include, path

from rest_framework.routers import DefaultRouter
from .views import (IngredientViewSet, RecipeViewSet,
                    TagViewSet, UserViewSet,
                    # FollowViewSet,
                    ShoppingCartViewSet, FavoritViewSet)
app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipes')
router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                FavoritViewSet, 'favorite')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                ShoppingCartViewSet, 'shopping_cart')
router.register('users', UserViewSet, 'users')


urlpatterns = (
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
)
