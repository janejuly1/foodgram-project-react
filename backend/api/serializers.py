from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from drf_extra_fields.fields import Base64ImageField

from foodgram.models import (Ingredient, Recipe, Tag,
                             Favourite, IngredientInRecipe,
                             ShoppingCart)
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
        fields = '__all__'


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


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()

    class Meta:
        exclude = ['author']
        model = Recipe


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField('_tags')
    is_favorited = serializers.SerializerMethodField('_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('_is_in_shopping_cart')

    def _is_favorited(self, recipe):
        if 'request' in self.context:
            request = self.context['request']
            if hasattr(request, 'user'):
                current_user = request.user
                if (current_user is not None
                        and not current_user.is_anonymous
                        and current_user.favourites.filter(
                            recipe=recipe).exists()):
                    return True

        return False

    def _is_in_shopping_cart(self, recipe):
        if 'request' in self.context:
            request = self.context['request']
            if hasattr(request, 'user'):
                current_user = request.user
                if (current_user is not None
                        and not current_user.is_anonymous
                        and current_user.shopping_cart.filter(
                            recipe=recipe).exists()):
                    return True

        return False

    def _tags(self, recipe):
        tags = []
        for tag in recipe.tags.all():
            tags.append({
                'id': tag.id,
                'name': tag.name,
                'color': tag.color_code,
                'slug': tag.id,
            })

        return tags

    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientInRecipe
        fields = '__all__'


class ShoppingCartSerializer(serializers.Serializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = '__all__'


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = '__all__'