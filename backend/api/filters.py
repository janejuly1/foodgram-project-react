import django_filters as df
from django.db.models import Q

from foodgram.models import Ingredient, Recipe


class RecipeFilter(df.FilterSet):
    author = df.NumberFilter(field_name='author__id', lookup_expr='exact')
    is_favorited = df.NumberFilter(method='_is_favorited')
    is_in_shopping_cart = df.NumberFilter(method='_is_in_shopping_cart')
    tags = df.AllValuesMultipleFilter(field_name='tags__slug')

    def __init__(self, *args, **kwargs):
        self.current_user = None
        if 'request' in kwargs:
            request = kwargs['request']
            if hasattr(request, 'user'):
                self.current_user = request.user

        super(RecipeFilter, self).__init__(*args, **kwargs)

    def _is_favorited(self, qs, name, value):
        if value == 1:
            return qs.filter(favourites__user=self.current_user)

        return qs.filter(~Q(favourites__user=self.current_user))

    def _is_in_shopping_cart(self, qs, name, value):
        if value == 1:
            return qs.filter(shopping_cart__user=self.current_user)

        return qs.filter(~Q(shopping_cart__user=self.current_user))

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class IngredientFilter(df.FilterSet):
    name = df.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Ingredient
        fields = ['name']
