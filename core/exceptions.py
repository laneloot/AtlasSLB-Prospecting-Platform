class ScraperError(Exception):
    pass

class RobotsBlockedError(ScraperError):
    pass

class RateLimitExceededError(ScraperError):
    pass

class ExtractionError(ScraperError):
    pass

class NormalizationError(ScraperError):
    pass
