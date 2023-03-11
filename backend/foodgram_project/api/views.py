from rest_framework import mixins, viewsets
from recipes.models import (
    Ingredient, Recipe, Tag
)
from .serializers import (
    IngredientSerializer,
    RecipeGetSerializer, RecipePostSerializer,
    TagSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipe."""
    queryset = Recipe.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipePostSerializer
        return RecipeGetSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context.update(self.kwargs)
        context['detail'] = self.detail
        return context
    

class TagViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet, mixins.RetrieveModelMixin
):
    """Вьюсет для модели Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet, mixins.RetrieveModelMixin
):
    """Вьюсет для модели Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
