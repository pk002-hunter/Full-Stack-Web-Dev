from django.db import models


class MedicalEntry(models.Model):
    """Stores medical entries for soldiers - persists across server restarts."""
    service_number = models.CharField(max_length=50, db_index=True)
    injury = models.CharField(max_length=200, default='Assessment')
    body_part = models.CharField(max_length=100, default='Unknown')
    treatment = models.CharField(max_length=500, blank=True, default='')
    details = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    confirmed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Medical Entries'

    def __str__(self):
        return f"{self.service_number} - {self.injury} ({self.body_part}) @ {self.timestamp}"

    def to_dict(self):
        return {
            'id': self.id,
            'service_number': self.service_number,
            'injury': self.injury,
            'body_part': self.body_part,
            'treatment': self.treatment,
            'details': self.details,
            'notes': self.notes,
            'confirmed': self.confirmed,
            'timestamp': self.timestamp.isoformat(),
        }
