import base64
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from recipes.models import (
    Favorite, Ingredient, IngredientsPerRecipe, Recipe, Tag, TagsOnRecipe, ShoppingCart
)
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
    # amount = serializers.IntegerField(source='per_recipe.amount')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('name', 'measurement_unit')
        model = Ingredient
        # extra_kwargs = {'amount': {'source': 'per_recipe.amount'}}

    def create(self, validated_data):
        ins = []
        print(self.context)
        print('Hello!')
        print(self.initial_data)
        amount = self.initial_data['amount']
        defaults = {
            'recipe_id': self.context.get('recipe_id'),
            'ingredient_id': self.initial_data['id'],
            'amount': amount
        }
        IngredientsPerRecipe.objects.filter(recipe_id=self.context.get('recipe_id'), ingredient_id=self.initial_data['id']).delete()
        instance = IngredientsPerRecipe.objects.create(recipe_id=self.context.get('recipe_id'), ingredient_id=self.initial_data['id'], amount=amount)
        ins.append(instance)
        return ins
    
    def update(self, instance, validated_data):
        ins = []
        item = self.initial_data
        amount = item['amount']
        IngredientsPerRecipe.objects.filter(recipe_id=self.context.get('recipe_id'), ingredient_id=item['id']).delete()
        instance = IngredientsPerRecipe.objects.create(recipe_id=self.context.get('recipe_id'), ingredient_id=item['id'], amount=amount)
        ins.append(instance)
        return ins
    
    def to_representation(self, value):
        print(self.context)
        print(value)
        ret = super().to_representation(value)
        try:
            amount = IngredientsPerRecipe.objects.get(ingredient_id=value.id, recipe_id=self.context.get('pk')).amount
            ret['amount'] = self.fields['amount'].to_representation(amount)
        except:
            print(f'value_id= {value.id}, pk= {self.context.get("pk")}')
        return ret
    
    """def _get_model_fields(self, field_names, declared_fields, extra_kwargs):
        model_fields = super()._get_model_fields(field_names, declared_fields, extra_kwargs)
        amount_field = IngredientsPerRecipe._meta.get_field('amount')
        model_fields['amount'] = amount_field
        return model_fields"""
    
    """def get_amount(self, obj):
        json = JSONRenderer().render(serializers.SlugRelatedField(
            slug_field='amount', queryset=IngredientsPerRecipe.objects.filter(
            ingredient_id=obj.id,
            recipe_id=self.context.get('recipe_id')
            )
        ))
        return json"""


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientsPerRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientsPerRecipe."""
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        fields = ('recipe', 'ingredient', 'amount')
        model = IngredientsPerRecipe

    """def get_recipe(self, obj):
        recipe = self.context.get('recipe_id')
        if recipe:
            return get_object_or_404(Recipe, id=recipe)
        return None"""


class TagsOnRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели TagsOnRecipe."""
    tag = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    recipe = serializers.SerializerMethodField()

    class Meta:
        fields = ('recipe', 'tag')
        model = TagsOnRecipe

    def get_recipe(self, obj):
        recipe = self.context.get('recipe_id')
        if recipe:
            return get_object_or_404(Recipe, id=recipe)
        return None



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
        return Favorite.objects.filter(recipe_id=obj.id, user=obj.author).exists()
    
    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(recipe_id=obj.id, user=obj.author).exists()
    
    def to_representation(self, value):
        self.context['pk'] = value.id
        ret = super().to_representation(value)
        return ret



class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления экземпляра модели Recipe."""
    # id = serializers.IntegerField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True)
    ingredients = IngredientSerializer(
        many=True, required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )

    class Meta:
        fields = ('id', 'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time', 'author')
        model = Recipe
        # extra_kwargs = {
        #     'ingredients': {'source': 'recipe__ingredients'},
        # }

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.tags.set(validated_data.get('tags', instance.tags))
        ing_data = self.initial_data.get('ingredients', instance.ingredients)
        print(ing_data)
        print('validated_data:')
        print(*validated_data.get("ingredients"))
        """instance.ingredients = validated_data.get('ingredients', instance.ingredients)
        for ingredient in ingredients:
            IngredientsPerRecipe.objects.create(**ingredient, recipe_id=instance.id)"""
        # instance.ingredients.set(*validated_data.get('ingredients', instance.ingredients))
        print(self.data.get('id'))
        for data in ing_data:
            serializer = IngredientSerializer(data=data, context={'recipe_id': self.data.get('id')})
            print(serializer)
            res = serializer.is_valid(raise_exception=True)
            print(serializer.errors)
            res_1 = serializer.save()
            print(res_1)
            print('I am here!')
        instance.save()
        return instance
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        print(tags_data)
        ing_data = self.initial_data.get('ingredients')
        print(ing_data)
        print(get_object_or_404(Ingredient, name='Тесто').id)
        # print(self.data.get('id'))
        print('ooo')
        recipe = Recipe.objects.create(**validated_data)
        for data in ing_data:
            serializer = IngredientSerializer(data=data, context={'recipe_id': recipe.id})
            print(serializer)
            res = serializer.is_valid(raise_exception=True)
            print(res)
            res_1 = serializer.save()
            print(res_1)
        recipe.tags.set(tags_data)
        return recipe
