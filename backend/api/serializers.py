from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from foodgram.models import Ingredient, Recipe, Tag, Favourite
from user.models import User, Follower
from rest_framework_simplejwt.serializers import \
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    username_field = 'email'


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('_is_subscribed')

    class Meta:
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        ]
        model = User

    def _is_subscribed(self, user):
        if 'request' in self.context:
            request = self.context['request']
            if hasattr(request, 'user'):
                current_user = request.user
                if (current_user is not None
                        and not current_user.is_anonymous
                        and current_user.following.filter(
                            author=user).exists()):
                    return True

        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())])

    username = serializers.RegexField(
        r'^[\w.@+-]+\z',
        required=True,
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())])

    first_name = serializers.CharField(required=True, max_length=150)

    last_name = serializers.CharField(required=True, max_length=150)

    password = serializers.CharField(required=True, max_length=150)

    def validate(self, attrs):
        if 'username' in attrs and attrs['username'] == 'me':
            raise ValidationError({'username': 'username cannot be me'})

        return super().validate(attrs)


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Recipe


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['recipe', 'ingredient']


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(many=True)
    # amount =

    def create(self, validated_data):
        return Ingredient.objects.create(**validated_data)


class ShoppingCartSerializer(serializers.Serializer):
    pass


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
