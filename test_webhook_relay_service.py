from webhook_relay_service import WebhookRelay, verify_signature


def test_signature_verifies():
    from webhook_relay_service import sign_payload

    sig = sign_payload("shh", b"payload", 1000)
    assert verify_signature("shh", b"payload", 1000, sig) is True
    assert verify_signature("shh", b"payload", 1001, sig) is False
    assert verify_signature("other", b"payload", 1000, sig) is False
    assert verify_signature("shh", b"tampered", 1000, sig) is False


def test_delivery_success_first_try():
    seen = {}

    def transport(url, headers, body):
        seen["headers"] = headers
        return True

    r = WebhookRelay("shh", max_attempts=3)
    res = r.deliver("evt-1", "https://cb.example", {"k": "v"}, transport)
    assert res["delivered"] is True
    assert res["attempts"] == 1
    assert seen["headers"]["X-Webhook-Timestamp"]


def test_retry_until_cap():
    calls = {"n": 0}

    def transport(url, headers, body):
        calls["n"] += 1
        return False

    r = WebhookRelay("shh", max_attempts=4, base_delay=0.001)
    res = r.deliver("evt-2", "https://cb.example", {"x": 1}, transport)
    assert res["delivered"] is False
    assert res["attempts"] == 4
    assert calls["n"] == 4


def test_history_recorded():
    r = WebhookRelay("shh", max_attempts=2, base_delay=0.001)
    r.deliver("evt-3", "https://cb.example", {"y": 2}, lambda *a: True)
    assert len(r.deliveries["evt-3"]) == 1
