"""HTTP transport that cannot route local text through proxies or redirects."""

import urllib.error
import urllib.request
from urllib.parse import urlparse


class RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        raise urllib.error.HTTPError(request.full_url, code, "Local service redirects are forbidden", headers, response)


def open_local(request: urllib.request.Request, *, timeout: float):
    """Open an HTTP loopback request with an explicit proxy-free transport."""
    parsed = urlparse(request.full_url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Local transport requires an HTTP loopback endpoint")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), RejectRedirects())
    return opener.open(request, timeout=timeout)
