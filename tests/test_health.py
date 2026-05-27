import json
import re

import pytest

from src.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Core contract: HTTP status and JSON body
# ---------------------------------------------------------------------------


def test_health_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_json_body_exact(client):
    resp = client.get("/health")
    assert resp.get_json() == {"status": "ok"}


def test_health_content_type_is_json(client):
    resp = client.get("/health")
    assert resp.content_type.startswith("application/json")


# ---------------------------------------------------------------------------
# CI health-check script contract
# The bash step in ci.yml validates the response with:
#   grep -q '"status".*"ok"'
# These tests make sure the serialised body satisfies that exact pattern.
# ---------------------------------------------------------------------------


def test_health_body_satisfies_ci_grep_pattern(client):
    """Response text must match the grep pattern used in the CI health-test step."""
    resp = client.get("/health")
    body = resp.get_data(as_text=True)
    assert re.search(r'"status".*"ok"', body), (
        f'Body {body!r} does not match CI grep pattern \'"status".*"ok"\''
    )


def test_health_body_contains_status_key(client):
    """The literal string '"status"' must appear in the response body."""
    resp = client.get("/health")
    body = resp.get_data(as_text=True)
    assert '"status"' in body


def test_health_body_contains_ok_value(client):
    """The literal string '"ok"' must appear in the response body."""
    resp = client.get("/health")
    body = resp.get_data(as_text=True)
    assert '"ok"' in body


# ---------------------------------------------------------------------------
# JSON structure and value correctness
# ---------------------------------------------------------------------------


def test_health_status_value_is_lowercase_ok(client):
    """status must be exactly 'ok', not 'OK', 'Ok', 'okay', etc."""
    resp = client.get("/health")
    assert resp.get_json()["status"] == "ok"


def test_health_response_is_parseable_json(client):
    resp = client.get("/health")
    body = resp.get_data(as_text=True)
    parsed = json.loads(body)
    assert isinstance(parsed, dict)


def test_health_status_field_present_in_json(client):
    resp = client.get("/health")
    data = resp.get_json()
    assert "status" in data


def test_health_response_has_no_extra_fields(client):
    """The health endpoint should only return the 'status' field — nothing more."""
    resp = client.get("/health")
    data = resp.get_json()
    assert set(data.keys()) == {"status"}


# ---------------------------------------------------------------------------
# HTTP method routing
# ---------------------------------------------------------------------------


def test_health_post_returns_405(client):
    resp = client.post("/health")
    assert resp.status_code == 405


def test_health_put_returns_405(client):
    resp = client.put("/health")
    assert resp.status_code == 405


def test_health_delete_returns_405(client):
    resp = client.delete("/health")
    assert resp.status_code == 405


# ---------------------------------------------------------------------------
# Negative / boundary cases
# ---------------------------------------------------------------------------


def test_unknown_route_returns_404(client):
    resp = client.get("/nonexistent")
    assert resp.status_code == 404


def test_health_with_trailing_slash_does_not_error(client):
    """Trailing-slash variant should either redirect (3xx) or return cleanly, not 500."""
    resp = client.get("/health/")
    assert resp.status_code != 500


def test_health_response_body_is_not_empty(client):
    resp = client.get("/health")
    assert len(resp.get_data(as_text=True).strip()) > 0


# ---------------------------------------------------------------------------
# Regression / additional confidence
# ---------------------------------------------------------------------------


def test_health_idempotent_across_multiple_calls(client):
    """Multiple consecutive calls must return identical results (no side-effects)."""
    responses = [client.get("/health") for _ in range(3)]
    bodies = [r.get_json() for r in responses]
    assert all(b == {"status": "ok"} for b in bodies), (
        f"Expected consistent responses, got: {bodies}"
    )


def test_health_ci_curl_body_extraction_matches_grep(client):
    """
    Simulates the CI script's curl + grep logic:
        RESPONSE = body + '\\n' + http_code
        HTTP_CODE = last line
        BODY = all lines except last

    Verifies BODY satisfies: grep -q '"status".*"ok"'
    """
    resp = client.get("/health")
    raw_body = resp.get_data(as_text=True)
    http_code = str(resp.status_code)

    # Replicate: curl -s -w '\n%{http_code}'
    simulated_curl_output = raw_body + "\n" + http_code
    lines = simulated_curl_output.splitlines()
    extracted_http_code = lines[-1]
    extracted_body = "\n".join(lines[:-1])

    assert extracted_http_code == "200"
    assert re.search(r'"status".*"ok"', extracted_body), (
        f"Body extracted by CI script does not match grep pattern: {extracted_body!r}"
    )
