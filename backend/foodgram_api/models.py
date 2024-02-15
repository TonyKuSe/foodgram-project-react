from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField('Название', max_length=150)
    description = models.TextField(
        'Описание', max_length=255,
        null=True, blank=True
    )
    date_creat = models.DateTimeField('Дата создания', auto_now_add=True)
    cooking_time = models.IntegerField('Время приготовления')
    image = models.ImageField(
        upload_to='recipe/images/',
        null=True,
        default=None
    )
    author = models.ForeignKey('Автор',
        'User', related_name='recipes',
        on_delete=models.PROTECT
    )
    tag = models.ManyToManyField(
        'Тег', 'Tag', related_name='recipes'
    )
    ingredient = models.ManyToManyField(
        'Ингредиент', 'Ingredient',
        through='RecipeIngredient',
        related_name='recipes'
    )
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Название', max_length=150)
    color = models.CharField('Цвет', max_length=16)
    date_creat = models.DateTimeField('Дата создания', auto_now_add=True)
    slug = models.SlugField('Slug тега',
                            unique=True,
                            max_length=50,
                            db_index=True)
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=150)
    date_creat = models.DateTimeField('Дата создания', auto_now_add=True)
    unit_size = models.CharField('Размер', max_length=10)
    
    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        'Ingredient', on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    unit_size = models.CharField('Размер', max_length=10)

    class Meta:
        ordering = ['recipe']

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class FavoritesUser(models.Model):
    user = models.ForeignKey('Пользователь',
        'User', related_name='recipes',
        on_delete=models.PROTECT
    )
    favorites = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['recipe']

    def __str__(self):
        return f'{self.user} {self.favorites}'


class RecipeIngredientUser(models.Model):
    user = models.ForeignKey('Пользователь',
        'User', related_name='recipes',
        on_delete=models.PROTECT
    )
    shoplist = models.ForeignKey('RecipeIngredient', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['recipe']

    def __str__(self):
        return f'{self.user} {self.favorites}'