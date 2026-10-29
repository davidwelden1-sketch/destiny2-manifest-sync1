import unittest
from urllib.error import HTTPError, URLError
from scripts.http_retry import fetch_with_retry


class Response:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self):
        return b"ok"


class TestHttpRetry(unittest.TestCase):
    def test_retries_500_then_succeeds(self):
        calls, sleeps = [], []
        def opener(request, timeout):
            calls.append((request.full_url, timeout))
            if len(calls) < 3:
                raise HTTPError(request.full_url, 500, "Bungie unavailable", {}, None)
            return Response()
        self.assertEqual(fetch_with_retry("https://www.bungie.net/Platform/Destiny2/Manifest/",
                                          user_agent="test", opener=opener, sleeper=sleeps.append), b"ok")
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [1, 2])

    def test_does_not_retry_auth_or_missing(self):
        for code in (400, 401, 403, 404):
            calls = []
            def opener(request, timeout):
                calls.append(1)
                raise HTTPError(request.full_url, code, "bad", {}, None)
            with self.assertRaises(HTTPError):
                fetch_with_retry("https://www.bungie.net/", user_agent="test", opener=opener,
                                 sleeper=lambda _: None)
            self.assertEqual(len(calls), 1)

    def test_bounded_retries_network_error(self):
        calls = []
        def opener(request, timeout):
            calls.append(1)
            raise URLError("temporary")
        with self.assertRaises(URLError):
            fetch_with_retry("https://www.bungie.net/", user_agent="test", attempts=2,
                             opener=opener, sleeper=lambda _: None)
        self.assertEqual(len(calls), 2)

    def test_invalid_attempts(self):
        with self.assertRaises(ValueError):
            fetch_with_retry("https://www.bungie.net/", user_agent="test", attempts=0)


if __name__ == "__main__":
    unittest.main()
