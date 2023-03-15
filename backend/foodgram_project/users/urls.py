from django.urls import include, path
from rest_framework import routers
from users.views import FollowViewSet, UserViewSet, obtain_token, revoke_token

app_name = 'users'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    path('users/subscriptions/',
         FollowViewSet.as_view({'get': 'list'}),
         name='subscriptions'),
    path('users/<int:user_id>/subscribe/',
         FollowViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='subscribe'),
    path('', include(router.urls)),
    path('auth/token/login/', obtain_token, name='obtain_token'),
    path('auth/token/logout/', revoke_token, name='revoke_token'),
]
