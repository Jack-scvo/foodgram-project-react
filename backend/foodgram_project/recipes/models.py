from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()
MIN_VALUE = 1
MAX_VALUE = 10000


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
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        ]
    )
    tags = models.ManyToManyField(Tag, through='TagsOnRecipe')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientsPerRecipe'
    )
    is_favorited = models.BooleanField('Есть в избранном', null=True)
    is_in_shopping_cart = models.BooleanField('Есть в корзине', null=True)
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.name


class IngredientsPerRecipe(models.Model):
    """Модель, релизующая связь многие-ко-многим Ингредиентов и Рецептов."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.SET_NULL, null=True,
        related_name='per_recipe'
    )
    amount = models.PositiveIntegerField('Количество в рецепте',
                                         validators=[
                                             MinValueValidator(MIN_VALUE),
                                             MaxValueValidator(MAX_VALUE)
                                         ])

    class Meta:
        ordering = ('recipe', 'ingredient', )
        unique_together = ('recipe', 'ingredient', )

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class TagsOnRecipe(models.Model):
    """Модель, релизующая связь многие-ко-многим Тегов и Рецептов."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ('recipe', 'tag', )

    def __str__(self):
        return f'{self.recipe} - {self.tag}'


class Favorite(models.Model):
    """Модель, хранящая данные об избранном."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('user', 'recipe', )

    def __str__(self):
        return f'{self.recipe} - {self.user}'


class ShoppingCart(models.Model):
    """Модель, хранящая данные о списке покупок."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('user', 'recipe', )

    def __str__(self):
        return f'{self.recipe} - {self.user}'
