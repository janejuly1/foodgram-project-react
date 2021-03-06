from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import Http404, StreamingHttpResponse
from django_filters import rest_framework as filters
from rest_framework import mixins, status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .serializers import (AuthorWithRecipesSerializer,
                          ChangePasswordSerializer, IngredientSerializer,
                          RecipeMinifiedSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, RegistrationSerializer,
                          TagSerializer, TokenObtainSerializer,
                          TokenSerializer, UserSerializer)
from foodgram.models import Favourite, Ingredient, Recipe, ShoppingCart, Tag
from user.models import Follower, User
from user.permissions import IsAuthorOrReadOnlyPermission


class TokenObtainView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token_obtain_serializer = TokenObtainSerializer(data=request.data)
        token_obtain_serializer.is_valid(raise_exception=True)

        validated_data = token_obtain_serializer.validated_data
        try:
            user = User.objects.filter(email=validated_data['email']).get()
        except ObjectDoesNotExist:
            raise ValidationError('пользователь не найден')

        if not user.check_password(validated_data['password']):
            raise ValidationError('пользователь не найден')

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            data=TokenSerializer({'auth_token': token.key}).data,
            status=status.HTTP_201_CREATED)


class TokenDeleteView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not request.user or request.user.is_anonymous or not request.auth:
            return Response(
                data={'detail': 'пользователь не авторизован'},
                status=status.HTTP_401_UNAUTHORIZED)

        request.auth.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(detail=False, url_path='me')
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = User.objects.create_user(
            email=data['email'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=data['password'],
        )
        user.save()

        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)


class TagViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = [IsAuthorOrReadOnlyPermission]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipeWriteSerializer

        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteOrShoppingCartManagerMixin:
    model = None

    def post(self, request, id):
        try:
            recipe = get_object_or_404(Recipe, id=id)
        except Http404:
            return Response({"error": "Рецепт не найден"},
                            status=status.HTTP_400_BAD_REQUEST)

        _, created = self.model.objects.get_or_create(
            user=request.user, recipe=recipe)
        if not created:
            return Response({"error": "Рецепт уже в списке избранного"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = RecipeMinifiedSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        try:
            recipe = get_object_or_404(Recipe, id=id)
            recipe_in_fav = get_object_or_404(
                self.model, user=request.user, recipe=recipe)
        except Http404:
            return Response({"error": "Рецепт не найден"},
                            status=status.HTTP_400_BAD_REQUEST)

        self.model.delete(recipe_in_fav)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(views.APIView, FavoriteOrShoppingCartManagerMixin):
    permission_classes = [IsAuthenticated]
    model = ShoppingCart

    def get(self, request):
        user = request.user
        recipes = user.shopping_cart.values('recipe').all()
        ingredients = (Ingredient.objects.
                       filter(recipe__in=recipes).
                       values('name', 'unit').
                       annotate(amount=Sum('ingredientinrecipe__amount')))

        rows = []
        for ingredient in ingredients:
            rows.append("{} {} {}\n".format
                        (ingredient['name'],
                         ingredient['amount'],
                         ingredient['unit']))

        response = StreamingHttpResponse(
            rows,
            content_type='text/plain; charset=utf8')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping list.txt"')
        return response


class FavoriteView(views.APIView, FavoriteOrShoppingCartManagerMixin):
    permission_classes = [IsAuthenticated]
    model = Favourite


class SubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AuthorWithRecipesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            pk__in=self.request.user.follower.values('author').all())


class SubscriptionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        if request.user == author:
            return Response({"error": "Нельзя подписаться на самого себя"},
                            status=status.HTTP_400_BAD_REQUEST)

        _, created = Follower.objects.get_or_create(user=request.user,
                                                    author=author)
        if not created:
            return Response({"error": "Уже подписан"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = AuthorWithRecipesSerializer(
            author, context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        if request.user == author:
            return Response({"errors": "Нельзя отписаться от самого себя"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            follower = Follower.objects.get(user=request.user, author=author)
        except ObjectDoesNotExist:
            return Response(
                {"errors": "Вы не были подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST)

        follower.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RegistrationView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = User.objects.create_user(
            email=data['email'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=data['password'],
        )
        user.save()

        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.data['current_password']):
            return Response(data={"current_password": ["Неверный пароль"]},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
