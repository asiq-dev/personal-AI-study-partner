from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):

    phone = models.CharField(max_length=15, blank=True, null=True)


    def __str__(self):
        return self.username