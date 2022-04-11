import django_filters as df
from foodgram.models import Recipe


class RecipeFilter(df.FilterSet):
    author = df.NumberFilter(field_name='author__id', lookup_expr='exact')
    is_favorited = df.NumberFilter(method='_is_favorited', lookup_expr='isnotnull')
    is_in_shopping_cart = df.NumberFilter(method='_is_in_shopping_cart', lookup_expr='isnotnull')
    tags = df.AllValuesMultipleFilter(field_name='tags__slug')

    def __init__(self, *args, **kwargs):
        self.current_user = None
        if 'request' in kwargs:
            request = kwargs['request']
            if hasattr(request, 'user'):
                self.current_user = request.user

        super(RecipeFilter, self).__init__(*args, **kwargs)

    def _is_favorited(self, qs, name, value):
        return qs.filter(favourites__user=self.current_user)

    def _is_in_shopping_cart(self, qs, name, value):
        return qs.filter(shopping_cart__user=self.current_user)

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
