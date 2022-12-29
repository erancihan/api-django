from django.db import models


class SoftDeleteManager(models.Manager):
    """
    so that when we get objects, non soft deleted ones always retrieved
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
