from django.db import models

from user.models import User


class Tag(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    color_code = models.CharField(max_length=6, verbose_name='HEX-код цвета')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    unit = models.CharField(max_length=100, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Recipe(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes')
    amount = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites'
    )
