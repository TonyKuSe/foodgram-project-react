from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Length
from PIL import Image


from .enums import Limits, Tuples


models.CharField.register_lookup(Length)

User = get_user_model()


class Recipe(models.Model):
    """Модель для рецептов."""

    name = models.CharField(
        verbose_name='Название блюда',
        max_length=Limits.MAX_LEN_NAME.value,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Тег',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ингредиенты блюда',
        through='RecipeIngredient',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )
    image = models.ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipe/images/',
        # TODO кодировка картинки в Base64
    )
    text = models.TextField(
        verbose_name='Описание блюда',
        max_length=Limits.MAX_LEN_TEXTFIELD.value,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=Limits.DEF_NUM,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
    
    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author}'


class Ingredient(models.Model):
    """Ингридиенты для рецепта."""

    name = models.CharField(
        verbose_name='Ингридиент',
        max_length=Limits.MAX_LEN_CHARFIELD_ING.value,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=Limits.MAX_MEASUREMENT_UNIT,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        # ordering = ('name',)
        

    def __str__(self) -> str:
        return f"{self.name} {self.measurement_unit}"


    def __str__(self) -> str:
        return f"{self.name}"


class RecipeIngredient(models.Model):
    """Количество ингридиентов в блюде.
    Модель связывает Recipe и Ingredient с указанием количества ингридиента.
    """

    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='В каких рецептах',
        related_name='rec_ingredient',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        verbose_name='Связанные ингредиенты',
        related_name='rec_ingredient',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=Limits.DEF_NUM,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipe',)
        
    def __str__(self) -> str:
        return f"{self.amount} {self.ingredient}"


class Tag(models.Model):
    """Тэги для рецептов."""

    name = models.CharField(
        verbose_name='Тэг',
        max_length=Limits.MAX_LEN_CHARFIELD.value,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=Limits.DEF_MAX_LEN,
        unique=True,
        db_index=False,
    )
    slug = models.CharField(
        verbose_name="Слаг тэга",
        max_length=Limits.MAX_LEN_CHARFIELD.value,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Favorites(models.Model):
    """Избранные рецепты."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Понравившиеся рецепты',
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"


class Carts(models.Model):
    """Рецепты в корзине покупок."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты в списке покупок',
        related_name='carts',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Владелец списка',
        related_name='carts',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"
