from rest_framework import permissions

from .models import Follower
from foodgram.models import Favourite, Recipe


class IsAuthorOrReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.is_admin:
            return True

        if ((type(obj) == Favourite
             or type(obj) == Recipe
             or type(obj) == Follower)
                and request.user.is_authenticated
                and request.user.is_admin):
            return True

        return (obj.author == request.user
                or request.method in permissions.SAFE_METHODS)
