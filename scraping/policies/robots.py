from reppy.robots import Robots
from urllib.parse import urlparse

class RobotsPolicy:
    def __init__(self, user_agent="AtlasSLB"):
        self.user_agent = user_agent
        self._cache = {}

    def is_allowed(self, url):
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        if robots_url not in self._cache:
            self._cache[robots_url] = Robots.fetch(robots_url)

        rules = self._cache[robots_url]
        return rules.allowed(url, self.user_agent)
