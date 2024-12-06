import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from models import UUIDModel


class User(AbstractUser, UUIDModel):
    email = models.EmailField(unique=True)

    packages_token = models.UUIDField(default=uuid.uuid4)
