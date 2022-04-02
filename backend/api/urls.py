from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'shopping_cart', ShoppingCartViewSet, basename='shopping_cart')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'ingredients', IngredientsViewSet, basename='ingredient')

urlpatterns = router.urls
