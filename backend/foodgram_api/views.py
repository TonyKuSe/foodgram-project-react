from http import HTTPMethod
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
from reviews.models import Carts, Favorites, Ingredient, Recipe, Tag
from reviews.svc import FoodFun
from users.models import Subscriptions
from django.shortcuts import get_object_or_404
from foodgram_config import settings
# from .mixins import AddDelViewMixin
from .paginators import PageLimitPagination
from .permissions import (AdminOrReadOnly, AuthorStaffOrReadOnly,
                          FoodDjangoModelPermissions, FoodIsAuthenticated,
                          AllowAnyMe, OwnerUserOrReadOnly, IsAuthenticated)
from users.serializers import (UserSubscribeSerializer,
                               UserSerializer, UserRetrieveSerializer, UserSetPasswordSerializer, FollowSerializer)
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer)
from django.views.generic import CreateView

User = get_user_model()

class UserViewSet(DjoserUserViewSet):

    pagination_class = PageLimitPagination
    permission_classes = ()
    filter_backends = (filters.SearchFilter,)

    # def get_queryset(self):
    #     if self.action == 'retrieve' and self.request.data is not None:
    #         return User.objects.filter(id=self.request.data['id'])
    #     return super().get_queryset()
    
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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Работет с игридиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = RecipeSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 
    