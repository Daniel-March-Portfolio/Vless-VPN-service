from uuid import uuid4

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, verbose_name="ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        abstract = True
