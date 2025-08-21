from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static
import random
import string


def generate_secret_code(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class CustomUserManager(BaseUserManager):
    def create_user(self, code, password=None, **extra_fields):
        if not code:
            raise ValueError("El usuario debe tener un código")
        if not extra_fields.get('first_name'):
            raise ValueError("El usuario debe tener un primer nombre.")
        if not extra_fields.get('last_name'):
            raise ValueError("El usuario debe tener un apellido.")

        extra_fields.setdefault('secret_code', generate_secret_code())

        user = self.model(code=code, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, code, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(code=code, password=password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    code = models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name="ID de usuario"
    )
    
    first_name = models.CharField(
        max_length=50,
        verbose_name=_("Primer nombre"),
        validators=[MinLengthValidator(2)],
    )

    last_name = models.CharField(
        max_length=50,
        verbose_name=_("Primer apellido"),
        validators=[MinLengthValidator(2)],
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    secret_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Código secreto"),
        help_text=_("Código de verificación para validación de identidad."),
    )

    is_seller = models.BooleanField(
        default=False,
        verbose_name=_("Es vendedor"),
        help_text=_("Indica si el usuario es un vendedor."),
    )

    cooperative_name = models.CharField(
        max_length=100,
        verbose_name=_("Nombre de la cooperativa"),
        help_text=_("Nombre de la cooperativa del vendedor."),
        blank=True,
        null=True,
    )

    cooperative_logo = models.ImageField(
        upload_to='cooperative_logos/',
        verbose_name=_("Logo de la cooperativa"),
        help_text=_("Logo de la cooperativa del vendedor."),
        blank=True,
        null=True,
    )

    credit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(50000)
        ],
        verbose_name=_("Crédito"),
    )

    debt = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(20000)
        ],
        verbose_name=_("Deuda"),
    )


    USERNAME_FIELD = 'code'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.first_name} {self.last_name or ''}".strip()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()
    
    def get_first_name(self):
        return self.first_name or ''
    
    def get_last_name(self):
        return self.last_name or ''
    
    def get_cooperative_logo_url(self):
        if self.cooperative_logo:
            return self.cooperative_logo.url
        return '/media/cooperative_logos/default.png'

    def get_cooperative_name(self):
        return self.cooperative_name 

    def save(self, *args, **kwargs):
        if not self.secret_code:
            self.secret_code = generate_secret_code()
        super().save(*args, **kwargs)
