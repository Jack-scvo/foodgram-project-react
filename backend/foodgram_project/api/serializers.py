from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .common import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientsPerRecipe, Recipe,
                            ShoppingCart, Tag)
from users.serializers import AuthorSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    id = serializers.IntegerField(read_only=True)
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('name', 'measurement_unit')
        model = Ingredient

    def to_representation(self, value):
        ret = super().to_representation(value)
        if self.context.get('recipe_id'):
            amount = IngredientsPerRecipe.objects.get(
                ingredient_id=value.id, recipe_id=self.context.get('recipe_id')
            ).amount
            ret['amount'] = self.fields['amount'].to_representation(amount)
        return ret


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения экземпляра модели Recipe."""
    id = serializers.IntegerField()
    tags = TagSerializer(read_only=True, many=True)
    author = AuthorSerializer()
    ingredients = IngredientSerializer(
        read_only=True, many=True,
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        model = Recipe

    def get_is_favorited(self, obj):
        if self.context['request_user'].is_authenticated:
            return Favorite.objects.filter(
                recipe_id=obj.id, user=self.context['request_user']
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context['request_user'].is_authenticated:
            return ShoppingCart.objects.filter(
                recipe_id=obj.id, user=self.context['request_user']
            ).exists()
        return False

    def to_representation(self, value):
        self.context['recipe_id'] = value.id
        return super().to_representation(value)


class TagPKField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, value):
        try:
            tag = Tag.objects.get(id=value.pk)
            serializer = TagSerializer(tag)
        except Exception as err:
            print(f'{err}')
        return serializer.to_representation(tag)


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления экземпляра модели Recipe."""
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True)
    ingredients = IngredientSerializer(
        many=True, required=True
    )
    tags = TagPKField(
        many=True, required=True, queryset=Tag.objects.all()
    )

    class Meta:
        fields = (
            'id', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time', 'author'
        )
        model = Recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.set(validated_data.get('tags', instance.tags))
        ing_data = self.initial_data.get('ingredients', instance.ingredients)
        ing_list = []
        IngredientsPerRecipe.objects.filter(
            recipe_id=instance.id,
        ).delete()
        for data in ing_data:
            ing_per_recipe = IngredientsPerRecipe(
                recipe_id=instance.id,
                ingredient_id=data['id'],
                amount=data['amount']
            )
            ing_list.append(ing_per_recipe)
        IngredientsPerRecipe.objects.bulk_create(ing_list)
        instance.save()
        return instance

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        validated_data.pop('ingredients')
        ing_data = self.initial_data.get('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        ing_list = []
        for data in ing_data:
            ing_per_recipe = IngredientsPerRecipe(
                recipe_id=recipe.id,
                ingredient_id=data['id'],
                amount=data['amount']
            )
            ing_list.append(ing_per_recipe)
        IngredientsPerRecipe.objects.bulk_create(ing_list)
        recipe.tags.set(tags_data)
        return recipe

    def to_representation(self, value):
        self.context['recipe_id'] = value.id
        return super().to_representation(value)
