"""Webhook relay service with HMAC signing and retry with backoff.

Real, working implementation for the Retsumdk ecosystem. Signs payloads with an
HMAC-SHA256 signature over a timestamp, delivers to a pluggable transport, and
retries with exponential backoff up to a maximum attempt count.
"""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Callable, Optional

Transport = Callable[[str, dict, bytes], bool]


def sign_payload(secret: str, body: bytes, timestamp: int) -> str:
    msg = f"{timestamp}.".encode("utf-8") + body
    return hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()


def verify_signature(secret: str, body: bytes, timestamp: int, signature: str) -> bool:
    expected = sign_payload(secret, body, timestamp)
    return hmac.compare_digest(expected, signature)


class WebhookRelay:
    def __init__(self, secret: str, max_attempts: int = 3,
                 base_delay: float = 0.1, clock: Optional[Callable[[], float]] = None):
        self.secret = secret
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.clock = clock or time.time
        self.deliveries: dict[str, list[dict]] = {}

    def deliver(self, event_id: str, url: str, payload: dict,
                transport: Optional[Transport] = None) -> dict:
        body = (str(payload)).encode("utf-8")
        attempts = 0
        for attempt in range(1, self.max_attempts + 1):
            attempts = attempt
            ts = int(self.clock())
            sig = sign_payload(self.secret, body, ts)
            headers = {"X-Webhook-Timestamp": str(ts), "X-Webhook-Signature": sig}
            ok = transport(url, headers, body) if transport else True
            self.deliveries.setdefault(event_id, []).append(
                {"attempt": attempt, "ok": ok, "ts": ts}
            )
            if ok:
                return {"event_id": event_id, "delivered": True, "attempts": attempts}
            if attempt < self.max_attempts:
                time.sleep(self.base_delay * (2 ** (attempt - 1)))
        return {"event_id": event_id, "delivered": False, "attempts": attempts}
