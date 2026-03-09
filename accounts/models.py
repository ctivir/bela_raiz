from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('salon', 'Salon Owner'),
        ('reseller', 'Reseller'),
        ('courier', 'Courier'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client'
    )

    phone_regex = RegexValidator(
        regex=r'^\+258\d{8,9}$',
        message="Phone number must be in format: '+258XXXXXXXXX'"
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=15,
        unique=True,
        help_text="Mozambican phone number in format +258XXXXXXXXX"
    )

    # Location fields for geolocation features
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # Profile completion
    is_profile_complete = models.BooleanField(default=False)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def is_salon_owner(self):
        return self.role == 'salon'

    @property
    def is_client(self):
        return self.role == 'client'

    @property
    def is_reseller(self):
        return self.role == 'reseller'

    @property
    def is_courier(self):
        return self.role == 'courier'
