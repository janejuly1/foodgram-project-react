from django.contrib import admin

from .models import Recipe, Ingredient, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author_username',
        'name',
    )
    list_filter = ('author__username', 'name', 'tags__name')
    readonly_fields = ['recipe_fav_count']

    def author_username(self, obj):
        return obj.author.username

    def tags_name(self, obj):
        tags_name = []
        for tag in obj.tags.all():
            tags_name.append(tag.name)

        return ', '.join(tags_name)

    def recipe_fav_count(self, obj):
        return obj.favourites.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'unit',
    )
    list_filter = ('name',)

class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    fields = (
        'name',
        'color_code',
        'slug',
    )

admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(Recipe)
admin.site.register(Ingredient, IngredientAdmin)
# admin.site.register(Ingredient)
admin.site.register(Tag, TagAdmin)
