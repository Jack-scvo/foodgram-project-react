from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models, transaction


class UserManager(BaseUserManager):
    "Менеджер кастомной модели пользователя."
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Нужно предоставить email!')
        try:
            with transaction.atomic():
                user = self.model(email=email, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except:
            raise

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password=password, **extra_fields)


class CustomUser(AbstractUser):
    "Кастомная модель пользователя."
    is_subscribed = models.BooleanField(null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.username)


CustomUser._meta.get_field('username').max_length = 150
CustomUser._meta.get_field('email').max_length = 254
CustomUser._meta.get_field('email')._unique = True
CustomUser._meta.get_field('password').max_length = 150
CustomUser._meta.get_field('first_name').max_length = 150
CustomUser._meta.get_field('last_name').max_length = 150


class Follow(models.Model):
    """Хранит данные о подписках."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Юзер, который подписывается'
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор, на которого подписываются'
    )

    class Meta:
        verbose_name = 'Подписки'
        ordering = ('user', 'author', )

    def __str__(self):
        return f'{self.user} follows {self.author}'
