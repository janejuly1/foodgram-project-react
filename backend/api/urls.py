from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ChangePasswordView, FavoriteView, IngredientsViewSet,
                    RecipeViewSet, ShoppingCartView, SubscriptionsViewSet,
                    SubscriptionView, TagViewSet, TokenDeleteView,
                    TokenObtainView, UserViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientsViewSet, basename='ingredient')

urlpatterns = [
    path(
        r'users/<int:user_id>/subscribe/',
        SubscriptionView.as_view(),
        name='subscribe'
    ),
    path(
        r'users/subscriptions/',
        SubscriptionsViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    path(
        r'recipes/download_shopping_cart/',
        ShoppingCartView.as_view(),
        name='download_shopping_cart'
    ),
    path(
        r'recipes/<int:id>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart',
    ),
    path(
        r'recipes/<int:id>/favorite/',
        FavoriteView.as_view(),
        name='favorite'
    ),
    path(
        r'users/set_password/',
        ChangePasswordView.as_view(),
        name='change_password'
    ),
    path(
        r'auth/token/login/',
        TokenObtainView.as_view(),
        name='token_obtain'
    ),
    path(
        r'auth/token/logout/',
        TokenDeleteView.as_view(),
        name='token_delete'
    ),
    path('', include(router.urls)),
]
