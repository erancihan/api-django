from django.db import models
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    """
    so that when we get objects, non soft deleted ones always retrieved
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    def get_deleted(self):
        return self.deleted_at is not None

    def set_deleted(self, d):
        if d and not self.deleted_at:
            self.deleted_at = timezone.now()
        elif not d and self.deleted_at:
            self.deleted_at = None

    deleted = property(get_deleted, set_deleted)

    class Meta:
        abstract = True
        permissions = [
            ('can_undelete', 'Can undelete this object'),
        ]
