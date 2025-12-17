from django.contrib import admin
from .models import Firm, Seed, ScrapeRun, ScrapeTarget

admin.register(Firm)
admin.register(Seed)
admin.register(ScrapeRun)
admin.register(ScrapeTarget)
