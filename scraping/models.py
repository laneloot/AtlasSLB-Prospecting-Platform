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

    # Operational tracking
    last_scraped_at = models.DateTimeField(null=True, blank=True)
    consecutive_failures = models.IntegerField(default=0)
    permanently_disabled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["active"]),
            models.Index(fields=["permanently_disabled"]),
        ]

class ScrapeRun(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_RUNNING = "RUNNING"
    STATUS_PARTIAL = "PARTIAL_SUCCESS"
    STATUS_FAILED = "FAILED"
    STATUS_SUCCESS = "SUCCESS"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_PARTIAL, "Partial Success"),
        (STATUS_FAILED, "Failed"),
        (STATUS_SUCCESS, "Success"),
    ]

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    dry_run = models.BooleanField(default=False)

    # Aggregates (critical)
    total_targets = models.IntegerField(default=0)
    succeeded_targets = models.IntegerField(default=0)
    failed_targets = models.IntegerField(default=0)

    # Diagnostics
    failure_reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]



class ScrapeTarget(models.Model):
    scrape_run = models.ForeignKey(
        ScrapeRun,
        on_delete=models.CASCADE,
        related_name="targets",
    )

    url = models.URLField()

    # Lifecycle
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    # Outcome
    success = models.BooleanField(default=False)
    http_status = models.IntegerField(null=True, blank=True)

    # Failure diagnostics
    error_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="ROBOTS_BLOCKED, TIMEOUT, EXTRACTION_ERROR, etc.",
    )
    error_message = models.TextField(blank=True)

    # Operational metadata
    retries = models.IntegerField(default=0)
    user_agent = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["success"]),
            models.Index(fields=["error_type"]),
        ]
