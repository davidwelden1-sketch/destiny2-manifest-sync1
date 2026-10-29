"""Bounded HTTP retry for transient Bungie API/CDN errors; never mask 4xx."""
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RETRYABLE_HTTP = frozenset({429, 500, 502, 503, 504})


def fetch_with_retry(url, *, user_agent, timeout=180, attempts=4, opener=urlopen, sleeper=time.sleep):
    if attempts < 1:
        raise ValueError("At least one HTTP attempt is required")
    request = Request(url, headers={"User-Agent": user_agent})
    for attempt in range(attempts):
        try:
            with opener(request, timeout=timeout) as response:
                return response.read()
        except HTTPError as error:
            if error.code not in RETRYABLE_HTTP or attempt == attempts - 1:
                raise
        except (URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
        sleeper(min(2 ** attempt, 8))
    raise AssertionError("Unreachable retry loop exit")
