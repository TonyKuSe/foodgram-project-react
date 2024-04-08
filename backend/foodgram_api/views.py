from django.http import HttpResponse
from django.db.models.aggregates import Sum
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from reviews.models import (Carts, Favorites,
                            Ingredient, Recipe,
                            Tag, RecipeIngredient)
from users.models import Subscriptions
from .permissions import AuthorStaffOrReadOnly, AdminOrReadOnly
from users.serializers import (ListUserSubscribeSerializer, UserMeSerializer,
                               UserSerializer, UserRetrieveSerializer,
                               UserSetPasswordSerializer, FollowSerializer)
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeSerializerList, FavoritRecipeSerializer,
                          CartsRecipeSerializer, TagSerializer)


User = get_user_model()


SERIALIZER_CLASSES = {
    'retrieve': UserRetrieveSerializer,
    'set_password': UserSetPasswordSerializer,
    'me': UserMeSerializer,
    'list': UserRetrieveSerializer,
}


class UserViewSet(DjoserUserViewSet):
    """Вьюсет работет с User"""

    filter_backends = (filters.SearchFilter,)

    def get_permissions(self):
        if self.action == 'retrieve':
            return [AllowAny()]
        return super().get_permissions()

    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(User, id=id)

    def get_serializer_class(self):
        return SERIALIZER_CLASSES.get(self.action, UserSerializer)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(AllowAny,)
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
        """
        Функция для выведения списка авторов
        на которых подписан пользователь
        """
        user = request.user
        queryset = user.publisher.all()
        pages = self.paginate_queryset(queryset)
        serializer = ListUserSubscribeSerializer(
            pages, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет работет с тэгами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет работет с игридиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет работет с Recipe."""

    permission_classes = (AuthorStaffOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author',)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        if self.request.query_params.get('is_in_shopping_cart') is not None:
            return queryset.filter(carts__user=self.request.user)
        if self.request.query_params.get('is_favorited') is not None:
            tags = self.request.query_params.getlist('tags')
            if not tags:
                return queryset.filter(favorites__user=self.request.user)
            return queryset.filter(
                favorites__user=self.request.user,
                tags__slug__in=tags
            ).distinct()
        elif self.request.query_params.get('tags') is not None:
            tags = self.request.query_params.getlist('tags')
            return queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializerList
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, id=self.kwargs.get('recipe_id'))

    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request):
        """Загружает файл со списком покупок"""
        text_final = []
        recipe_ingred = RecipeIngredient.objects.filter(
            recipe__carts__user=self.request.user.id).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    amount=Sum('amount'))
        for text in recipe_ingred:
            text_f = (
                f'{text.setdefault("ingredient__name",["Нет ингредиента"])} '
                f'{text.setdefault("ingredient__measurement_unit",["Нет"])} '
                f'- {text.setdefault("amount",["Нет массы"])} '
            )
            text_final.append(text_f)
        return HttpResponse(
            text_final, content_type="text.txt; charset=utf-8"
        )


class FavoritViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с подписками."""
    serializer_class = FavoritRecipeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        return Favorites.objects.select_related(
            'recipe', 'user').filter(recipe=recipe_id)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(user=self.request.user, recipe=recipe)

    @action(methods=('delete',), detail=True)
    def delete(self, request, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        instance = Favorites.objects.select_related(
            'recipe', 'user').filter(recipe=recipe_id)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с моделью покупки."""

    serializer_class = CartsRecipeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)

    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        new_queryset = Carts.objects.select_related(
            'recipe', 'user').filter(recipe=recipe_id)
        return new_queryset

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(user=self.request.user, recipe=recipe)

    @action(methods=('delete',), detail=True)
    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        instance = Carts.objects.select_related(
            'recipe', 'user').filter(recipe=recipe_id)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
