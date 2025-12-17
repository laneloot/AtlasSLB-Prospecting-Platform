from scraping.models import Seed

class SeedService:
    def get_active_seeds(self, limit=None):
        qs = Seed.objects.filter(
            active=True,
            permanently_disabled=False,
        ).order_by("id")

        if limit:
            qs = qs[:limit]

        return list(qs)
