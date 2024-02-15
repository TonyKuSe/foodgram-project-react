from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.managers import FoodUserManager


class FoodUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    name  = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    role = models.CharField()
    subs = models.ForeignKey('User', on_delete=models.CASCADE)
    favorites =  models.ManyToManyField('Recipe',
                                          through='FavoritesUser')
    shopping_list = models.ManyToManyField('RecipeIngredient',
                                          through='RecipeIngredientUser')
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = FoodUserManager()

    def __str__(self):
        return self.email