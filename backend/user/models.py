from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    GUEST_ROLE = 'guest'
    USER_ROLE = 'user'
    ADMIN_ROLE = 'admin'
    ROLE = [(GUEST_ROLE, 'guest'),
            (USER_ROLE, 'user'),
            (ADMIN_ROLE, 'admin')]

    first_name = models.CharField(max_length=150,
                                  null=True, blank=True)
    last_name = models.CharField(max_length=150,
                                 null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE,
                            default=GUEST_ROLE, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.ADMIN_ROLE or self.is_superuser

    @property
    def is_user(self):
        return self.role == self.USER_ROLE


class Follower(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
