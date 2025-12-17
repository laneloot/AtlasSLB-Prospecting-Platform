from django.db import models
from core.enums import FirmType, SectorTag

class Firm(models.Model):
    name = models.CharField(max_length=255, unique=True)
    firm_type = models.CharField(max_length=50, choices=FirmType.choices)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Seed(models.Model):
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE)
    url = models.URLField()
    active = models.BooleanField(default=True)


class ScrapeRun(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50)
    dry_run = models.BooleanField(default=False)


class ScrapeTarget(models.Model):
    scrape_run = models.ForeignKey(ScrapeRun, on_delete=models.CASCADE)
    url = models.URLField()
    success = models.BooleanField(default=False)
    error = models.TextField(blank=True)
