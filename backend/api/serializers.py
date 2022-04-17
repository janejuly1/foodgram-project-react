from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import \
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer

from foodgram.models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                             ShoppingCart, Tag)
from user.models import Follower, User


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        data = super().validate(attrs)
        data.pop('refresh')

        return data


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('_is_subscribed')

    class Meta:
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        ]
        model = User

    def _is_subscribed(self, user):
        current_user = get_user_from_serializer_context(self)
        if (current_user is not None
                and not current_user.is_anonymous
                and current_user.following.filter(
                    author=user).exists()):
            return True

        return False


class TagSerializer(serializers.ModelSerializer):
    color = serializers.CharField(source='color_code')

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())])

    username = serializers.RegexField(
        r'^[\w.@+-]+',
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


class CustomField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return {self.field_name: data}


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'amount']


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = IngredientInRecipeWriteSerializer(source="ingredientinrecipe_set",many=True)
    image = Base64ImageField()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredientinrecipe_set')
        recipe = super().create(validated_data)
        for ingredient in ingredients:
            IngredientInRecipe.objects.get_or_create(
                ingredient_id=ingredient['ingredient']['id'],
                amount=ingredient['amount'],
                recipe=recipe)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredientinrecipe_set')
        recipe = super().create(validated_data)
        for ingredient in ingredients:
            IngredientInRecipe.objects.get_or_create(
                ingredient_id=ingredient['ingredient']['id'],
                amount=ingredient['amount'],
                recipe=recipe)

        return recipe

    class Meta:
        exclude = ['author']
        model = Recipe


class AuthorWithRecipesSerializer(UserSerializer):
    DEFAULT_RECIPES_LIMIT = 3

    recipes = serializers.SerializerMethodField('_recipes')
    recipes_count = serializers.SerializerMethodField('_recipes_count')

    def _recipes(self, user):
        limit = self.DEFAULT_RECIPES_LIMIT
        if 'request' in self.context:
            request = self.context['request']
            if 'recipes_limit' in request.GET:
                limit = int(request.GET['recipes_limit'])

        recipes = []
        for recipe in user.recipes.all()[:limit]:
            serializer = RecipeMinifiedSerializer(recipe)
            recipes.append(serializer.data)

        return recipes

    def _recipes_count(self, user):
        return user.recipes.count()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count']


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.unit')

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeReadSerializer(many=True, source='ingredientinrecipe_set')
    is_favorited = serializers.SerializerMethodField('_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('_is_in_shopping_cart')

    def _is_favorited(self, recipe):
        current_user = get_user_from_serializer_context(self)
        if (current_user is not None
                and not current_user.is_anonymous
                and current_user.favourites.filter(
                    recipe=recipe).exists()):
            return True

        return False

    def _is_in_shopping_cart(self, recipe):
        current_user = get_user_from_serializer_context(self)
        if (current_user is not None
                and not current_user.is_anonymous
                and current_user.shopping_cart.filter(
                    recipe=recipe).exists()):
            return True

        return False

    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()


def get_user_from_serializer_context(serializer):
    if 'request' in serializer.context:
        request = serializer.context['request']
        if hasattr(request, 'user'):
            return request.user

    return None
