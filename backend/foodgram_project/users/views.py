from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, generics, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser
from .serializers import AuthorSerializer, SignUpSerializer, ObtainTokenSerializer


class UserViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin,  viewsets.GenericViewSet
):
    """Вьюсет для модели CustomUser."""
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action in ['create',]:
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

    """def perform_create(self, serializer):
        new_user = serializer.save()
        unique_code = default_token_generator.make_token(new_user)
        serializer.save(password=unique_code)"""

    @action(methods=['get',], detail=False, url_path='me')
    def get_me(self, request):
        user = get_object_or_404(CustomUser, pk=request.user.pk)
        serializer = AuthorSerializer(user, context={'request_user': request.user})
        return Response(serializer.data)


@api_view(['POST'])
def obtain_token(request):
    """View-функция для получения токена авторизации."""
    serializer = ObtainTokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    asking_user = get_object_or_404(
        CustomUser, email=serializer.data['email']
    )
    """if not default_token_generator.check_token(
            asking_user, token=serializer.data['password']):
        return HttpResponseBadRequest('Неверный пароль.')"""
    refresh = RefreshToken.for_user(asking_user)
    token_data = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    return Response({'auth_token': token_data['access']}, status.HTTP_200_OK)
