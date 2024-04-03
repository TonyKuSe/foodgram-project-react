from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Length
from django.utils.translation import gettext_lazy as _

from reviews import texts
from reviews.enums import Limits

models.CharField.register_lookup(Length)


class FoodUser(AbstractUser):
    """
    Модель пользователя.
    При создании пользователя все поля обязательны для заполнения.
    """
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=Limits.MAX_LEN_EMAIL.value,
        unique=True,
        help_text=texts.USER_HELP_EMAIL,
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=Limits.MAX_LEN_USERNAME.value,
        unique=True,
        help_text=texts.USER_HELP_USERNAME,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=Limits.MAX_LEN_FIRST_NAME.value,
        help_text=texts.USER_HELP_F_NAME,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=Limits.MAX_LEN_LAST_NAME.value,
        help_text=texts.USER_HELP_L_NAME,
    )
    password = models.CharField(
        verbose_name=_('Пароль'),
        max_length=128,
        help_text=texts.USER_HELP_PASSWORD,
    )
    is_active = models.BooleanField(
        verbose_name='Активирован',
        default=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ('username',)
        constraints = (
            models.CheckConstraint(
                check=models.Q(username__length__gte=Limits.DEF_MIN_LEN.value),
                name='User',
            ),
        )

    def __str__(self) -> str:
        return f'{self.email}, {self.username}'


class Subscriptions(models.Model):
    """Подписки пользователей друг на друга."""
    user = models.ForeignKey(
        'FoodUser',
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        'FoodUser',
        verbose_name='Автор рецепта',
        related_name='publisher',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        models.constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='Signed',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='No self sibscription'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} подписан {self.author}'
