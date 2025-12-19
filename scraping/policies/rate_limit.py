import time
from urllib.parse import urlparse
from collections import defaultdict

class RateLimiter:
    def __init__(self, min_delay_seconds=5):
        self.min_delay = min_delay_seconds
        self.last_access = defaultdict(float)

    def wait(self, url):
        domain = urlparse(url).netloc
        elapsed = time.time() - self.last_access[domain]
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_access[domain] = time.time()
