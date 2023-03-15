import base64

from django.core.files.base import ContentFile
from recipes.models import (Favorite, Ingredient, IngredientsPerRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import AuthorSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    id = serializers.IntegerField(read_only=True)
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('name', 'measurement_unit')
        model = Ingredient

    def create(self, validated_data):
        ins = []
        amount = self.initial_data['amount']
        IngredientsPerRecipe.objects.filter(
            recipe_id=self.context.get('recipe_id'),
            ingredient_id=self.initial_data['id']
        ).delete()
        instance = IngredientsPerRecipe.objects.create(
            recipe_id=self.context.get('recipe_id'),
            ingredient_id=self.initial_data['id'], amount=amount
        )
        ins.append(instance)
        return ins

    def update(self, instance, validated_data):
        ins = []
        item = self.initial_data
        amount = item['amount']
        IngredientsPerRecipe.objects.filter(
            recipe_id=self.context.get('recipe_id'), ingredient_id=item['id']
        ).delete()
        instance = IngredientsPerRecipe.objects.create(
            recipe_id=self.context.get('recipe_id'),
            ingredient_id=item['id'], amount=amount
        )
        ins.append(instance)
        return ins

    def to_representation(self, value):
        ret = super().to_representation(value)
        try:
            amount = IngredientsPerRecipe.objects.get(
                ingredient_id=value.id, recipe_id=self.context.get('recipe_id')
            ).amount
            ret['amount'] = self.fields['amount'].to_representation(amount)
        except:
            print("No amount")
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
        return Favorite.objects.filter(
            recipe_id=obj.id, user=obj.author
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(
            recipe_id=obj.id, user=obj.author
        ).exists()

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
        for data in ing_data:
            serializer = IngredientSerializer(
                data=data, context={'recipe_id': self.data.get('id')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        instance.save()
        return instance

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ing_data = self.initial_data.get('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for data in ing_data:
            serializer = IngredientSerializer(
                data=data, context={'recipe_id': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        recipe.tags.set(tags_data)
        return recipe

    def to_representation(self, value):
        self.context['recipe_id'] = value.id
        return super().to_representation(value)
