import django_filters as df
from foodgram.models import Recipe


class RecipeFilter(df.FilterSet):
    author = df.NumberFilter(field_name='author__id', lookup_expr='exact')
    is_favorited = df.BooleanFilter(method='_is_favorited')
    is_in_shopping_cart = df.BooleanFilter(method='_is_in_shopping_cart')
    tags = df.AllValuesMultipleFilter(field_name='tags__slug')

    def _is_favorited(self, qs, name, value):
        return qs.filter(favourites__gt=1)

    def _is_in_shopping_cart(self, qs, name, value):
        return qs.filter(shopping_cart__gt=1)

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']
