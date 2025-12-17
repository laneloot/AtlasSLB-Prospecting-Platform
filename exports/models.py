from django.db import models
from core.enums import FirmType, SectorTag

class PlatformCompany(models.Model):
    firm_name = models.CharField(max_length=255)
    firm_type = models.CharField(max_length=50, choices=FirmType.choices)
    sector_tag = models.CharField(max_length=50, choices=SectorTag.choices)

    name = models.CharField(max_length=255)
    website = models.URLField(blank=True)

    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    source_url = models.URLField()
    source_type = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    locations_count = models.IntegerField(null=True, blank=True)
    real_estate_intensive = models.BooleanField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
