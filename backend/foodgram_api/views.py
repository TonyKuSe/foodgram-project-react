# from http import HTTPMethod
# from datetime import datetime
from django.http import HttpResponse
# from django.shortcuts import render
# from django.core.mail import send_mail
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
from .permissions import (AdminOrReadOnly, AuthorStaffOrReadOnly,
                          FoodDjangoModelPermissions, FoodIsAuthenticated,
                          AllowAnyMe, OwnerUserOrReadOnly, IsAuthenticated, IsAuthenticatedOrReadOnly)
from users.serializers import (UserSubscribeSerializer, UserMeSerializer,
                               UserSerializer, UserRetrieveSerializer, UserSetPasswordSerializer, FollowSerializer)
from .serializers import (IngredientSerializer, RecipeSerializer, RecipeSerializerList, FavoritRecipeSerializer,
                          CartsRecipeSerializer, TagSerializer)
from django.views.generic import CreateView

User = get_user_model()

class UserViewSet(DjoserUserViewSet):

    pagination_class = PageLimitPagination
    permission_classes = ()
    filter_backends = (filters.SearchFilter,)
    
    def get_object(self):
        id = self.kwargs.get('id')
        obj = get_object_or_404(User, id=id)
        return obj
    
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
        for recipe_id in Carts.objects.all().filter(user=self.request.user).values('recipe'): 
            for text in RecipeIngredient.objects.all().filter(
                recipe__id=recipe_id['recipe']).values(
                    'ingredient__name', 'ingredient__measurement_unit').annotate(Sum('amount')):
                text_f = (f'{text.setdefault("ingredient__name",["default"])} {text.setdefault("ingredient__measurement_unit",["default"])} - {text.setdefault("amount__sum",["default"])} ')
                text_final.append(text_f)
        response = HttpResponse(
            text_final, content_type="text.txt; charset=utf-8"
        )
        return response


class FavoritViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с моделью ."""
    serializer_class = FavoritRecipeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)
    
    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        new_queryset = Favorites.objects.select_related('recipe', 'user').filter(recipe=recipe_id)
        return new_queryset
    
    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(user=self.request.user, recipe=recipe)
    
    @action(methods=('delete',), detail=True)
    def delete(self):
        recipe_id = self.kwargs.get('recipe_id')
        instance = Favorites.objects.select_related('recipe', 'user').filter(recipe=recipe_id)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с моделью ."""
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
