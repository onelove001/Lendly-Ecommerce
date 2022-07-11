from re import M
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy


class MyUserManager(BaseUserManager):

    def _create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)

        if kwargs.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff True")
        if kwargs.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser True")
        return self._create_user(email, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=False)
    is_staff = models.BooleanField(
        ugettext_lazy("Staff Status"), default=False,
        help_text=ugettext_lazy("Designates whether user can log in the site")
    )
    is_active = models.BooleanField(
        ugettext_lazy("Acitve Status"),
        default=True,
        help_text=ugettext_lazy("Designates whether user the user should be treated as active")
    )

    USERNAME_FIELD = "email"
    objects = MyUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    username = models.CharField(max_length=50, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    address = models.TextField(max_length=260, blank=True)
    city = models.CharField(max_length=40, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=40, blank=True)
    phone = models.CharField(max_length=18, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}'s profile"

    def is_fully_filled(self):
        fields_name = [f.name for f in self._meta.get_fields()]
        for field in fields_name:
            value = getattr(self, field)
            if value is None or value == "":
                return False
        return True
