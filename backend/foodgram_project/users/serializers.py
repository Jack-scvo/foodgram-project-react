from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import CustomUser, Follow


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор для модели CustomUser."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        fields = ('email', 'username', 'id', 'first_name',
                  'last_name', 'is_subscribed', 'password') 
        model = CustomUser
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context['request_user']
        if obj !=  user:
            try:
                res = Follow.objects.filter(user=user, author=obj).exists()
                return res
            except:
                return False
        else:
            return False
    

class SignUpSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'password': {'required': True},
        }

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Выбранное имя пользователя недоступно.')
        return value
    
    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ObtainTokenSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=150, required=True)
    email = serializers.CharField(max_length=150, required=True)
    