from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True)
    # Store whether the user agreed to marketing emails
    marketing_opt_in = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.get_username()

# Create your models here.
