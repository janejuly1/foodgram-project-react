from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import GenericAPIView

from .serializers import *
from user.models import *
from foodgram.models import *


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    @action(detail=False, url_path='me')
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class TagViewSet(viewsets.ViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pass


class RecipeViewSet(viewsets.ViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pass


class ShoppingCartViewSet(viewsets.ViewSet):
    queryset = IngredientInRecipe.objects.all()
    serializer_class = ShoppingCartSerializer
    pass


class FavoriteViewSet(viewsets.ViewSet):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
    pass


class SubscriptionViewSet(viewsets.ViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    pass


class IngredientsViewSet(viewsets.ViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RegistrationView(GenericAPIView):
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
