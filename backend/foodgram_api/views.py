from http import HTTPMethod
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.db.models.aggregates import Count, Sum

from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import decorators, response, status, viewsets, filters, views, mixins, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from reviews.enums import Tuples, UrlQueries
from reviews.models import Carts, Favorites, Ingredient, Recipe, Tag, RecipeIngredient
from users.models import Subscriptions
from django.shortcuts import get_object_or_404
from foodgram_config import settings
from rest_framework_simplejwt.tokens import RefreshToken
# from .mixins import AddDelViewMixin
from .paginators import PageLimitPagination
from .permissions import (AdminOrReadOnly, AuthorStaffOrReadOnly,
                          FoodDjangoModelPermissions, FoodIsAuthenticated,
                          AllowAnyMe, OwnerUserOrReadOnly, IsAuthenticated)
from users.serializers import (UserSubscribeSerializer,
                               UserSerializer, UserRetrieveSerializer, UserSetPasswordSerializer, FollowSerializer)
from .serializers import (IngredientSerializer, RecipeSerializer, RecipeSerializerList, FavoritRecipeSerializer,
                          CartsRecipeSerializer, TagSerializer)
from django.views.generic import CreateView

User = get_user_model()

class UserViewSet(DjoserUserViewSet):

    pagination_class = PageLimitPagination
    permission_classes = ()
    filter_backends = (filters.SearchFilter,)
    
    def get_serializer_class(self):
        if self.action == 'retrieve' and self.request.data is not None:
            return UserRetrieveSerializer
        elif self.action == 'set_password':
            return UserSetPasswordSerializer
        return UserSerializer
    
    
    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):

        user = request.user
        queryset = Subscriptions.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = UserSubscribeSerializer(
            pages, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class CreateDeleteSubscribe(
        generics.RetrieveDestroyAPIView, generics.CreateAPIView):
    
    serializer_class = FollowSerializer
    
    def get_object(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def perform_destroy(self, instance):
        self.request.user.publisher.filter(author=instance).delete()


class FollowViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (AllowAnyMe,)
    filter_backends = (filters.SearchFilter,)


class TagViewSet(viewsets.ModelViewSet):
    """Работает с тэгами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    """Работет с игридиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = (AdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # permission_classes = (IsAuthenticated,)
    
    def get_serializer_class(self):
        if self.action == 'create' or 'update':
            if self.basename == 'favorite':
                return FavoritRecipeSerializer
            return RecipeSerializer
        return RecipeSerializerList
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user, id=self.kwargs.get('recipe_id'))

    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request: WSGIRequest) -> Response:
        """Загружает файл со списком покупок"""
        user = self.request.user
        recipe_list = Carts.objects.all().filter(user=user).values('recipe_id')
        shopping_list = []
        for recipe_id in recipe_list:
            shopping_list.append(RecipeIngredient.objects.all().filter(
                recipe__id=recipe_id['recipe_id']).values(
                    'ingredient__name', 'ingredient__measurement_unit').annotate(Sum('amount')))
        response = HttpResponse(
            shopping_list, content_type="text.txt; charset=utf-8"
        )
        return response



class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с моделью Comments."""
    serializer_class = CartsRecipeSerializer
    permission_classes = (IsAuthenticated,)

    http_method_names = ('post', 'delete', 'get')
    
    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(user=self.request.user, recipe=recipe)
