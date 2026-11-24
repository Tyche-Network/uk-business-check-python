"""UK business check API client: Companies House, HMRC VAT and charity status in one call.

Docs: https://api.tychelabs.net/docs/business  Product page: https://api.tychelabs.net/business
Standard library only (Python 3.9+).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterable, Optional

__all__ = ["BusinessCheck", "TycheApiError", "verify_webhook"]
__version__ = "1.0.0"


class TycheApiError(Exception):
    def __init__(self, status: int, code: str, message: str, body: Any = None):
        super().__init__(message)
        self.status, self.code, self.body = status, code, body


class _Client:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.tychelabs.net", timeout: float = 15.0):
        self.api_key = api_key or os.environ.get("TYCHE_API_KEY")
        if not self.api_key:
            raise ValueError("Pass api_key or set TYCHE_API_KEY. Get a free key at https://api.tychelabs.net/signup")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _req(self, method: str, path: str, body: Any = None) -> Any:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base_url + path, data=data, method=method)
        req.add_header("x-api-key", self.api_key)
        req.add_header("user-agent", f"tyche-python/{__version__}")
        if data is not None:
            req.add_header("content-type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                raw = res.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            try:
                j = json.loads(e.read() or b"{}")
            except ValueError:
                j = {}
            err = j.get("error") or {}
            raise TycheApiError(e.code, err.get("code", "http_error"), err.get("message", f"HTTP {e.code}"), j) from None

    def list_watches(self) -> Any:
        return self._req("GET", "/v1/watches")

    def delete_watch(self, watch_id: str) -> None:
        self._req("DELETE", "/v1/watches/" + urllib.parse.quote(watch_id, safe=""))

    def account(self) -> Any:
        return self._req("GET", "/v1/account")


class BusinessCheck(_Client):
    """Client for the UK business check API.

    >>> api = BusinessCheck()          # reads TYCHE_API_KEY
    >>> c = api.check("16716814", vat="GB553557881")["data"]
    >>> c["company"]["status"], c["risk"], c["flags"]
    """

    def check(self, company_number: str, vat: Optional[str] = None, include: Optional[Iterable[str]] = None,
              eori: Optional[str] = None) -> Any:
        q = {}
        if vat:
            q["vat"] = vat
        if eori:
            q["eori"] = eori
        if include is not None:
            q["include"] = ",".join(include)
        path = "/v1/companies/" + urllib.parse.quote(company_number, safe="")
        return self._req("GET", path + ("?" + urllib.parse.urlencode(q) if q else ""))

    def search(self, name: str) -> Any:
        return self._req("GET", "/v1/companies/search?" + urllib.parse.urlencode({"q": name}))

    def vat(self, vat_number: str) -> Any:
        return self._req("GET", "/v1/vat/" + urllib.parse.quote(vat_number, safe=""))

    def eori(self, eori_number: str) -> Any:
        """Validate a UK (GB/XI) or EU EORI number."""
        return self._req("GET", "/v1/eori/" + urllib.parse.quote(eori_number, safe=""))

    def watch(self, company_number: str, url: str, events: Optional[Iterable[str]] = None, email_digest: bool = False) -> Any:
        body = {"companyNumber": company_number, "url": url}
        if events is not None:
            body["events"] = list(events)
        if email_digest:
            body["emailDigest"] = True
        return self._req("POST", "/v1/watches", body)


def verify_webhook(raw_body: bytes, header: str, secret: str, tolerance_secs: int = 300) -> bool:
    """Check the tyche-signature header of a webhook. raw_body must be the exact bytes received."""
    try:
        parts = dict(p.split("=", 1) for p in header.split(","))
        ts = int(parts["t"])
    except (KeyError, ValueError):
        return False
    if abs(time.time() - ts) > tolerance_secs:
        return False
    expected = hmac.new(secret.encode(), f"{ts}.".encode() + raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, parts.get("v1", ""))
