from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'ingredients', IngredientsViewSet, basename='ingredient')

urlpatterns = [
    path(
        r'users/<int:user_id>/subscribe/',
        SubscriptionView.as_view(),
        name='subscribe'
    ),
    path(
        r'users/subscriptions/',
        SubscriptionView.as_view(),
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
    path('', include(router.urls)),
]
