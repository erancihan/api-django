from django.db import models
from server.core.models import Model


class Post(Model):
    title = models.TextField()
    content = models.TextField(blank=True)

    class Meta(Model.Meta):
        ordering = ["created_at"]
