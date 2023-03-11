from django.urls import include, path
from rest_framework import routers
from api.views import RecipeViewSet, TagViewSet, IngredientViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
