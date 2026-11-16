import re
import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


def normalize_phone(value):
    """'+995 555-12-34-56' -> '995555123456' (digits only), so one number has one spelling."""
    return re.sub(r"[\s\-()+]", "", value or "")


phone_validator = RegexValidator(r"^\d{9,15}$", "ტელეფონის ნომერი უნდა შედგებოდეს 9-დან 15 ციფრამდე.")


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create(self, phone, password, **extra):
        phone = normalize_phone(phone)
        if not phone:
            raise ValueError("ტელეფონის ნომერი აუცილებელია.")
        user = self.model(phone=phone, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create(phone, password, **extra)

    def create_superuser(self, phone, password=None, **extra):
        extra["is_staff"] = True
        extra["is_superuser"] = True
        return self._create(phone, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):

    phone = models.CharField("ტელეფონი", max_length=15, unique=True, validators=[phone_validator])
    first_name = models.CharField("სახელი", max_length=60)
    last_name = models.CharField("გვარი", max_length=60)
    email = models.EmailField("ელფოსტა")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    class Meta:
        verbose_name = "მომხმარებელი"
        verbose_name_plural = "მომხმარებლები"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def initials(self):
        return f"{self.first_name[:1]}.{self.last_name[:1]}".upper()


class ApiToken(models.Model):

    key = models.CharField(max_length=40, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_tokens")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(20)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.phone}: {self.key[:6]}…"
