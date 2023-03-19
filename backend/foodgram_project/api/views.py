from django.http import HttpResponse
from recipes.models import (Favorite, Ingredient, IngredientsPerRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.serializers import SimpleRecipeSerializer
from users.views import LimitPageNumberPagination

from .permissions import IsAdminOrOwner
from .serializers import (IngredientSerializer, RecipeGetSerializer,
                          RecipePostSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipe."""
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipePostSerializer
        return RecipeGetSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request_user'] = self.request.user
        context.update(self.kwargs)
        context['detail'] = self.detail
        context.update(self.request.query_params)
        return context

    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated, IsAdminOrOwner]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.query_params.get('is_in_shopping_cart'):
                qs = ShoppingCart.objects.filter(
                    user=self.request.user
                ).values_list('recipe_id', flat=True)
                queryset = Recipe.objects.filter(id__in=qs)
            elif self.request.query_params.get('is_favorited'):
                qs = Favorite.objects.filter(
                    user=self.request.user
                ).values_list('recipe_id', flat=True)
                queryset = Recipe.objects.filter(id__in=qs)
            else:
                queryset = Recipe.objects.all()
        else:
            queryset = Recipe.objects.all()
        if self.request.query_params.get('tags'):
            tags = []
            tags = self.request.query_params.getlist('tags')
            for tag in tags:
                queryset = queryset.filter(tags__slug__contains=tag)
        return queryset


class TagViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для модели Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]


class IngredientViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для модели Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name', )
    permission_classes = [AllowAny, ]


class FavoriteViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для избранного."""
    queryset = Favorite.objects.all()
    serializer_class = SimpleRecipeSerializer

    def create(self, request, *args, **kwargs):
        Favorite.objects.get_or_create(
            recipe_id=self.kwargs.get('recipe_id'), user=request.user
        )
        instance = Recipe.objects.get(id=self.kwargs.get('recipe_id'))
        data = {
            'id': instance.pk,
            'name': instance.name,
            'image': instance.image,
            'cooking_time': instance.cooking_time
        }
        serializer = SimpleRecipeSerializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = Favorite.objects.get(
                recipe_id=self.kwargs.get('recipe_id'), user=request.user
            )
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            print('No favorite object')


class ShoppingCartViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для добавления и удаления из корзины."""
    queryset = ShoppingCart.objects.all()
    serializer_class = SimpleRecipeSerializer

    def create(self, request, *args, **kwargs):
        ShoppingCart.objects.get_or_create(
            recipe_id=self.kwargs.get('recipe_id'), user=request.user
        )
        instance = Recipe.objects.get(id=self.kwargs.get('recipe_id'))
        data = {
            'id': instance.pk,
            'name': instance.name,
            'image': instance.image,
            'cooking_time': instance.cooking_time
        }
        serializer = SimpleRecipeSerializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = ShoppingCart.objects.get(
                recipe_id=self.kwargs.get('recipe_id'), user=request.user
            )
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            print('No shopping cart object')


@api_view()
def download_cart(request):
    """View-функция для скачивания списка ингредиентов."""
    qs = ShoppingCart.objects.filter(user=request.user).values_list(
        'recipe_id', flat=True
    )
    recipes = Recipe.objects.filter(id__in=qs)
    ingredients_list = {}
    for recipe in recipes:
        for ingredient in recipe.ingredients.all():
            amount = IngredientsPerRecipe.objects.get(
                recipe=recipe, ingredient=ingredient
            ).amount
            key = f'{ingredient.name} ({ingredient.measurement_unit}) - '
            ingredients_list[key] = ingredients_list.get(key, 0) + amount
    response = HttpResponse(content_type='text/plain; charset=UTF-8')
    response['Content-Disposition'] = 'attachment; filename=ingredients.txt'
    for name, amount in ingredients_list.items():
        response.write(name + str(amount) + '\n')
    return response
