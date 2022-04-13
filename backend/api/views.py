import csv

from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import Http404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters

from .filters import RecipeFilter
from .serializers import *
from user.models import *
from foodgram.models import *
from user.permissions import (IsAuthorOrReadOnlyPermission,
                              IsAuthorPermission, IsAdminOrReadOnly)
# from ..user.models import *
# from ..foodgram.models import *
# from ..user.permissions import (IsAuthorOrReadOnlyPermission,
#                               IsAuthorPermission, IsAdminOrReadOnly)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    @action(detail=False, url_path='me')
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipeWriteSerializer

        return RecipeReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        recipe = get_object_or_404(Recipe, pk=serializer.data.get('id'))
        read_serializer = RecipeReadSerializer(
            recipe,
            context=self.get_serializer_context()
        )

        return Response(read_serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        recipe = get_object_or_404(Recipe, pk=serializer.data.get('id'))
        read_serializer = RecipeReadSerializer(
            recipe,
            context=self.get_serializer_context()
        )

        return Response(read_serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ShoppingCartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ingredients = {}
        for recipe in Recipe.objects.filter(
                shopping_cart__user=request.user).all():
            for ingredient in recipe.ingredients.all():
                if ingredient.ingredient.id not in ingredients:
                    ingredients[ingredient.ingredient.id] = [
                        ingredient.ingredient, ingredient.amount]
                else:
                    ingredients[ingredient.ingredient.id][1] += ingredient.amount

        response = Response(content_type='text/plain; charset=utf8')
        response['Content-Disposition'] = 'attachment; filename="shopping list.txt"'

        writer = csv.writer(response)
        for ingredient in ingredients.values():
            writer.writerow(["%s %s %d".format(ingredient[0].name, ingredient[0].unit, ingredient[1])])

        return response

    def post(self, request, id):
        try:
            recipe = get_object_or_404(Recipe, id=id)
        except Http404:
            return Response({"error": "Рецепт не найден"},
                            status=status.HTTP_400_BAD_REQUEST)

        _, created = ShoppingCart.objects.get_or_create(
            user=request.user, recipe=recipe)
        if not created:
            return Response({"error": "Рецепт уже в списке покупок"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = RecipeMinifiedSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        try:
            recipe = get_object_or_404(Recipe, id=id)
            recipe_in_cart = get_object_or_404(
                ShoppingCart, user=request.user, recipe=recipe)
        except Http404:
            return Response({"error": "Рецепт не найден"},
                            status=status.HTTP_400_BAD_REQUEST)

        ShoppingCart.delete(recipe_in_cart)

        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission, )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return Favourite.objects.filter(recipe=recipe)

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)


class SubscriptionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        if request.user == author:
            return Response({"error": "Нельзя подписаться на самого себя"},
                            status=status.HTTP_400_BAD_REQUEST)

        _, created = Follower.objects.get_or_create(user=request.user, author=author)
        if not created:
            return Response({"error": "Уже подписан"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AuthorWithRecipesSerializer(
            author, context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RegistrationView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = User(
            email=data['email'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=data['password'],
        )
        user.save()

        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
