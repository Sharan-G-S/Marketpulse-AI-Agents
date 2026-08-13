"""
MarketPulse — HTTP Connection Pool Manager
Provides reusable HTTP session pooling with keep-alive headers for high-throughput API calls.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

_HTTP_SESSION = None


def get_http_session() -> requests.Session:
    """Returns a singleton requests.Session with connection pooling and retries."""
    global _HTTP_SESSION
    if _HTTP_SESSION is None:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=20)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({"User-Agent": "MarketPulse/2.0 (Enterprise AI Agent)"})
        _HTTP_SESSION = session
    return _HTTP_SESSION
