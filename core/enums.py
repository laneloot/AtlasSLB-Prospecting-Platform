from django.db import models

class FirmType(models.TextChoices):
    PE = "PE", "Private Equity"
    INDUSTRIAL_ROLLUP = "INDUSTRIAL_ROLLUP", "Industrial Roll-Up"
    INDUSTRIAL_SERVICES = "INDUSTRIAL_SERVICES", "Industrial Services"
    SPECIALTY_MANUFACTURING = "SPECIALTY_MANUFACTURING", "Specialty Manufacturing"
    HEALTHCARE_ROLLUP = "HEALTHCARE_ROLLUP", "Healthcare Roll-Up"
    HOLDCO = "HOLDCO", "HoldCo"
    DIVERSIFIED = "DIVERSIFIED", "Diversified"


class SectorTag(models.TextChoices):
    INDUSTRIAL = "INDUSTRIAL"
    HEALTHCARE = "HEALTHCARE"
    FOOD_BEVERAGE = "FOOD_BEVERAGE"
    MANUFACTURING = "MANUFACTURING"
    SPECIALTY = "SPECIALTY"
    OTHER = "OTHER"
