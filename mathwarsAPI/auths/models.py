from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UsersManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError("You are not enter Email")
        if not username:
            raise ValueError("You are not enter password")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password):
        return self._create_user(email, username, password, total=0, win=0, lose=0, percent=0)

    def create_superuser(self, email, username, password):
        return self._create_user(email, username, password, is_staff=True, is_superuser=True)


class Users(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    total = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    lose = models.IntegerField(default=0)
    percent = models.IntegerField(default=0)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    objects = UsersManager()

    def __str__(self):
        return self.username


class RefreshTokenManager(models.Manager):
    def create_refresh_token(self, user):
        refresh_token = self.model(user=user)
        refresh_token.save(using=self._db)
        return refresh_token


class RefreshTokenModel(models.Model):
    user = models.OneToOneField('Users', on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255, unique=True)
    objects = RefreshTokenManager()
