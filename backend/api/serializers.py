from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer)

from foodgram.models import Ingredient, IngredientInRecipe, Recipe, Tag
from user.models import User
from .utils import get_user_from_serializer_context


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


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'amount']


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = IngredientInRecipeWriteSerializer(
        source="ingredientinrecipe_set", many=True)
    image = Base64ImageField()

    def validate_tags(self, data):
        if not data:
            raise ValidationError('Добавьте хотя бы один тэг')

        if self.instance:
            for tag in data:
                if self.instance.tags.filter(tag=tag).exists():
                    raise ValidationError('Такой тэг уже существует')

        return data

    def validate_ingredients(self, data):
        if not data:
            raise ValidationError('Добавьте хотя бы один ингредиент')

        ids = []
        for ingredient in data:
            if ingredient['amount'] <= 0:
                raise ValidationError('Количество должно быть больше 0')

            if ingredient['ingredient']['id'] in ids:
                raise ValidationError('Вы пытаетесь добавить ингредиент '
                                      'больше одного раза')

            if (self.instance and
                    self.instance.ingredients.filter(
                        pk=ingredient['ingredient']['id']).exists()):
                raise ValidationError('Такой ингредиент уже добавлен')

            ids.append(ingredient['ingredient']['id'])

        return data

    def validate_cooking_time(self, data):
        if data < 1:
            raise ValidationError(
                'Время приготовления должно быть больше 1'
            )
        return data

    def create_ingredient_in_recipe(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientInRecipe.objects.get_or_create(
                ingredient_id=ingredient['ingredient']['id'],
                amount=ingredient['amount'],
                recipe=recipe)

    def create(self, validated_data):
        ingredients = []
        if 'ingredientinrecipe_set' in validated_data:
            ingredients = validated_data.pop('ingredientinrecipe_set')

        recipe = super().create(validated_data)

        self.create_ingredient_in_recipe(ingredients, recipe)

        return recipe

    def update(self, recipe, validated_data):
        ingredients = []
        if 'ingredientinrecipe_set' in validated_data:
            ingredients = validated_data.pop('ingredientinrecipe_set')

        recipe = super().update(recipe, validated_data)

        if len(ingredients) > 0:
            IngredientInRecipe.objects.filter(recipe=recipe).delete()

            self.create_ingredient_in_recipe(ingredients, recipe)

        return recipe

    class Meta:
        exclude = ['author']
        model = Recipe

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


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

        return RecipeMinifiedSerializer(
            user.recipes.all()[:limit],
            many=True).data

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
    ingredients = IngredientInRecipeReadSerializer(
        many=True, source='ingredientinrecipe_set')
    is_favorited = serializers.SerializerMethodField('_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        '_is_in_shopping_cart')

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
