from rest_framework.exceptions import NotFound, ValidationError

from user.models import User


class AuthBackend:
    def authenticate(self, request, email=None, password=None):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotFound('user not found')

        if not user.check_password(password):
            raise ValidationError({'password': 'invalid password'})

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
