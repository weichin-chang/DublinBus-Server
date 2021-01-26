from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    # Email id filed
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)
    # Phone number
    phone = models.CharField(null=True, max_length=255)
    # All require filed [Firstname and Lastname are already present in model)
    REQUIRED_FIELDS = ['username','phone', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    def get_username(self):
        return self.email