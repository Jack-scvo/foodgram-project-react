from recipes.models import Recipe
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
        try:
            user = self.context['request_user']
        except:
            return False
        if obj != user:
            try:
                return Follow.objects.filter(user=user, author=obj).exists()
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


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=150, required=True)
    current_password = serializers.CharField(max_length=150, required=True)


class LimitListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = super().to_representation(data)
        try:
            limit = int(self.context.get('recipes_limit'))
            data = data[:limit]
        except Exception as err:
            print(f'{err}')
        return super().to_representation(data)


class SimpleRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для подписок, избранного и корзины."""

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe
        list_serializer_class = LimitListSerializer


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""
    recipes = SimpleRecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.IntegerField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('username', )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        try:
            ret['recipes_count'] = self.fields[
                'recipes_count'
            ].to_representation(instance.recipes_count)
        except:
            ret['recipes_count'] = self.fields[
                'recipes_count'
            ].to_representation(instance.recipes.count())
        return ret

    def get_is_subscribed(self, obj):
        user = self.context['request_user']
        if obj != user:
            try:
                return Follow.objects.filter(user=user, author=obj).exists()
            except:
                return False
        else:
            return False

    def save(self, **kwargs):
        user_id = kwargs.get('user_id')
        self.instance = CustomUser.objects.get(id=user_id)
        try:
            Follow.objects.get_or_create(
                author_id=user_id, user=self.context['request_user']
            )
        except:
            print('Oups')
        return self.instance
