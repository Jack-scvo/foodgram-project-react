from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientsPerRecipe, Recipe,
                            ShoppingCart, Tag, TagsOnRecipe)

admin.site.register(Favorite)
admin.site.register(Tag)
admin.site.register(IngredientsPerRecipe)
admin.site.register(TagsOnRecipe)
admin.site.register(ShoppingCart)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientsPerRecipe
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'text', 'name', 'author', 'cooking_time',
    )
    readonly_fields = ('fav_count',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = (RecipeIngredientInline, )

    def fav_count(self, obj):
        return f'{Favorite.objects.filter(recipe_id=obj.id).count()}'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
