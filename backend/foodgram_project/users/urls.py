from django.urls import include, path
from rest_framework import routers
from users.views import UserViewSet, obtain_token

app_name = 'users'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/login/', obtain_token, name='obtain_token'),
]
