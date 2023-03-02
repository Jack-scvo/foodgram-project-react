from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()
MIN_VALUE_SCORE = 1


class Tag(models.Model):
    """Модель, хранящая данные о тегах."""
    name = models.CharField('Название тега', max_length=200)
    color = models.CharField('Цвет', max_length=7, default='#FF0000')
    slug = models.SlugField('Слаг', unique=True, max_length=50)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name
    

class Ingredient(models.Model):
    """Модель, хранящая данные об ингредиентах."""
    name = models.CharField('Название ингредиента', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=20)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name
    

class Recipe(models.Model):
    """Модель, хранящая данные о рецептах."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор')
    name = models.CharField('Название рецепта', max_length=200)
    text = models.TextField('Описание рецепта')
    image = models.ImageField(
        'Картинка',
        upload_to='images'
        )
    cooking_time = models.PositiveIntegerField(
        'Время готовки', validators=[
        MinValueValidator(MIN_VALUE_SCORE),
        ]
    )
    tags = models.ManyToManyField(Tag, through='TagsOnRecipe')
    ingredients = models.ManyToManyField(Ingredient, through='IngredientsPerRecipe')
    is_favorited = models.BooleanField('Есть в избранном')
    is_in_shopping_cart = models.BooleanField('Есть в корзине')

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name
    

class IngredientsPerRecipe(models.Model):
    """Модель, релизующая связь многие-ко-многим Ингредиентов и Рецептов."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField('Количество в рецепте')

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class TagsOnRecipe(models.Model):
    """Модель, релизующая связь многие-ко-многим Тегов и Рецептов."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.recipe} - {self.tag}'
    

class Favorite(models.Model):
    """Модель, хранящая данные об избранном."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} - {self.user}'
