from django.db.models import Count
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import (BlacklistedToken,
                                                             OutstandingToken)
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser, Follow
from users.serializers import (AuthorSerializer, FollowSerializer,
                               ObtainTokenSerializer, SetPasswordSerializer,
                               SignUpSerializer)


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Вьюсет для модели CustomUser."""
    queryset = CustomUser.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'get_set_password']:
            return [AllowAny(), ]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create']:
            return SignUpSerializer
        return AuthorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK,
                        headers=headers)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request_user'] = self.request.user
        return context

    @action(methods=['get', ], detail=False, url_path='me')
    def get_me(self, request):
        user = get_object_or_404(CustomUser, pk=request.user.pk)
        serializer = AuthorSerializer(
            user, context={'request_user': request.user}
        )
        return Response(serializer.data)

    @action(methods=['post', ], detail=False, url_path='set_password')
    def get_set_password(self, request):
        user = get_object_or_404(CustomUser, pk=request.user.pk)
        serializer = SetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        if not user.check_password(
            serializer.validated_data['current_password']
        ):
            return HttpResponseBadRequest('Неверный пароль.')
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def obtain_token(request):
    """View-функция для получения токена авторизации."""
    serializer = ObtainTokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    asking_user = get_object_or_404(
        CustomUser, email=serializer.data['email']
    )
    refresh = RefreshToken.for_user(asking_user)
    token_data = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    return Response({'auth_token': token_data['access']}, status.HTTP_200_OK)


@api_view(['POST'])
def revoke_token(request):
    """View-функция для удаления токена авторизации."""
    tokens = OutstandingToken.objects.filter(user_id=request.user.id)
    for token in tokens:
        t, _ = BlacklistedToken.objects.get_or_create(token=token)
    tokens.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class LimitPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class FollowViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                    mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для Подписок."""
    serializer_class = FollowSerializer
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        qs = self.request.user.follower.values_list('author_id', flat=True)
        authors = CustomUser.objects.annotate(
            recipes_count=Count('recipes')
        ).filter(id__in=qs)
        return authors

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request_user'] = self.request.user
        context['recipes_limit'] = self.request.query_params.get(
            'recipes_limit'
        )
        return context

    def perform_create(self, serializer):
        serializer.save(user_id=self.kwargs.get('user_id'))

    def destroy(self, request, *args, **kwargs):
        instance = Follow.objects.get(
            author_id=self.kwargs['user_id'], user=request.user
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
