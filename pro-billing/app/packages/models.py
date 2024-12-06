from django.db import models

from models import TimestampModel, UUIDModel


class Package(TimestampModel, UUIDModel):
    name = models.SlugField(unique=True)
    repo_url = models.URLField(unique=True)

    def __str__(self):
        return self.name

    @property
    def repo_full_name(self):
        return "/".join(self.repo_url.rstrip("/").split("/")[-2:])
