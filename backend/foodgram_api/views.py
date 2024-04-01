# from http import HTTPMethod
# from datetime import datetime
from django.http import HttpResponse
# from django.shortcuts import render
# from django.core.mail import send_mail
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.db.models.aggregates import Count, Sum

from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import decorators, response, status, viewsets, filters, views, mixins, generics
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework.routers import APIRootView
# from reviews.enums import Tuples, UrlQueries
from reviews.models import Carts, Favorites, Ingredient, Recipe, Tag, RecipeIngredient
from users.models import Subscriptions
from django.shortcuts import get_object_or_404
from foodgram_config import settings
from rest_framework_simplejwt.tokens import RefreshToken
# from .mixins import AddDelViewMixin
from .paginators import PageLimitPagination
# from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        DjangoModelPermissions,
                                        IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly)
from .permissions import (AdminOrReadOnly, AuthorStaffOrReadOnly,
                          FoodDjangoModelPermissions, FoodIsAuthenticated,
                          AllowAnyMe, OwnerUserOrReadOnly, IsAuthenticatedOrReadOnly)
from users.serializers import (ListUserSubscribeSerializer, UserMeSerializer,
                               UserSerializer, UserRetrieveSerializer, UserSetPasswordSerializer, FollowSerializer)
from .serializers import (IngredientSerializer, RecipeSerializer, RecipeSerializerList, FavoritRecipeSerializer,
                          CartsRecipeSerializer, TagSerializer)
from django.views.generic import CreateView

User = get_user_model()


class UserViewSet(DjoserUserViewSet):

    pagination_class = PageLimitPagination
    # permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    
    def get_permissions(self):
        if self.action == 'retrieve':
            return [AllowAny()]
        return super().get_permissions()

    def get_object(self):
        id = self.kwargs.get('id')
        obj = get_object_or_404(User, id=id)
        return obj
    
    def get_serializer_class(self):
        if self.action == 'retrieve' and self.request.data is not None:
            return UserRetrieveSerializer
        elif self.action == 'set_password':
            return UserSetPasswordSerializer
        elif self.action == 'me':
            return UserMeSerializer
        elif self.action == 'list':
            return UserRetrieveSerializer
        return UserSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        """Подписаться на пользователя."""
        author = get_object_or_404(User, id=kwargs.get('id'))
        request.data['author'] = author
        serializer = FollowSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        """Отписать на пользователя."""
        user = request.user
        author_id = kwargs['id']
        if get_object_or_404(
            Subscriptions,
            user=user,
            author_id=author_id
        ).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Функция для выведения списка авторов на которых подписан пользователь"""
        user = request.user
        queryset = Subscriptions.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = ListUserSubscribeSerializer(
            pages, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """Работает с тэгами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Работет с игридиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorStaffOrReadOnly,)
    permission_classes = (AllowAny,)
    def get_serializer_class(self):
        if self.action == 'create' or 'update':
            return RecipeSerializer
        return RecipeSerializerList

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, id=self.kwargs.get('recipe_id'))

    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request: WSGIRequest) -> Response:
        """Загружает файл со списком покупок"""
        text_final = list()
        recipe_ingred = RecipeIngredient.objects.filter(
            recipe__carts__user=self.request.user.id).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    amount=Sum('amount'))
        for text in recipe_ingred:
            text_f = (
                f'{text.setdefault("ingredient__name",["default"])} '
                f'{text.setdefault("ingredient__measurement_unit",["default"])} '
                f'- {text.setdefault("amount",["default"])} '
            )
            text_final.append(text_f)
        response = HttpResponse(
            text_final, content_type="text.txt; charset=utf-8"
        )
        return response


class FavoritViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с моделью ."""
    serializer_class = FavoritRecipeSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        new_queryset = Favorites.objects.select_related('recipe', 'user').filter(recipe=recipe_id)
        return new_queryset
    
    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(user=self.request.user, recipe=recipe)
    
    @action(methods=('delete',), detail=True)
    def delete(self, request, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        instance = Favorites.objects.select_related('recipe', 'user').filter(recipe=recipe_id)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с моделью покупки."""
    serializer_class = CartsRecipeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)

    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        new_queryset = Carts.objects.select_related('recipe', 'user').filter(recipe=recipe_id)
        return new_queryset
    
    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(user=self.request.user, recipe=recipe)
    
    @action(methods=('delete',), detail=True)
    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        instance = Carts.objects.select_related('recipe', 'user').filter(recipe=recipe_id)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
