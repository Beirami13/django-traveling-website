
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):

    def create_user(self, phone_number, full_name, password=None):

        if not phone_number:
            raise ValueError("Users must have a phone number")

        if not full_name:
            raise ValueError("Users must have a full name")

        user = self.model(
            phone_number=phone_number,
            full_name=full_name,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, phone_number, full_name, password=None):

        user = self.create_user(
            phone_number=phone_number,
            full_name=full_name,
            password=password,
        )

        user.is_admin = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        null=True,
        blank=True,
        unique=True,
    )

    image = models.ImageField(
        upload_to="profiles/images",
        blank=True,
        null=True,
    )

    full_name = models.CharField(max_length=100)

    phone_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="phone number",
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.phone_number

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin


class OTP(models.Model):

    token = models.CharField(max_length=100, unique=True)

    phone_number = models.CharField(
        max_length=100,
        verbose_name="phone number",
    )

    code = models.SmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    objects = models.Manager()

    def __str__(self):
        return self.phone_number

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at


class Address(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    city = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    zip_code = models.CharField(max_length=20)

    objects = models.Manager()

    class Meta:
        unique_together = ("user", "city", "address", "zip_code")

    def __str__(self):
        return f"{self.city} - {self.address}"
