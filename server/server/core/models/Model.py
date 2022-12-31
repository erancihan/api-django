from django.db import models
from django.utils import timezone

from server import settings
from server.core.managers import SoftDeleteManager


class Model(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self):
        if getattr(settings, "DEFAULT_IS_SOFT_DELETE", True):
            self.soft_delete()
        else:
            self.hard_delete()

    def hard_delete(self):
        super().delete()

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
