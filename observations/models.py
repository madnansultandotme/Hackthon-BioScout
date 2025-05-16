from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

class Observation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='observations')
    species_name = models.CharField(max_length=255)
    date_observed = models.DateField()
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='observations/images/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    ai_suggestion = models.CharField(max_length=255, blank=True, null=True)
    ai_confidence = models.FloatField(blank=True, null=True)
    community_validations = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Validate date_observed is not in the future
        if self.date_observed and self.date_observed > timezone.now().date():
            raise ValidationError({'date_observed': 'Observation date cannot be in the future'})
        
        # Validate location is not empty
        if not self.location.strip():
            raise ValidationError({'location': 'Location cannot be empty'})
        
        # Validate species name is not empty
        if not self.species_name.strip():
            raise ValidationError({'species_name': 'Species name cannot be empty'})

    def save(self, *args, **kwargs):
        # If date_observed is not set, use current date
        if not self.date_observed:
            self.date_observed = timezone.now().date()
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.species_name} ({self.location}) by {self.user.username}"
