import json
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from rules import evaluate, load_rules

REPO_ROOT = Path(__file__).resolve().parent.parent


def make_email(sender="", subject="", body="", days_old=0):
    return SimpleNamespace(
        sender=sender,
        subject=subject,
        body=body,
        date_received=datetime.now() - timedelta(days=days_old),
    )


def write_rules(tmp_path, rules):
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(rules))
    return path


def test_load_rules_reads_bundled_example():
    rules = load_rules(REPO_ROOT / "rules.json")
    assert rules["predicate"] in {"all", "any"}
    assert rules["conditions"]
    assert rules["actions"]


def test_load_rules_rejects_unknown_predicate(tmp_path):
    path = write_rules(tmp_path, {"predicate": "some", "conditions": []})
    with pytest.raises(ValueError, match="predicate"):
        load_rules(path)


def test_load_rules_rejects_missing_predicate(tmp_path):
    path = write_rules(tmp_path, {"conditions": []})
    with pytest.raises(ValueError, match="predicate"):
        load_rules(path)


def test_load_rules_rejects_unknown_operator(tmp_path):
    path = write_rules(
        tmp_path,
        {
            "predicate": "all",
            "conditions": [{"field": "sender", "operator": "regex", "value": "x"}],
        },
    )
    with pytest.raises(ValueError, match="Invalid operator: regex"):
        load_rules(path)


def test_contains_is_case_insensitive():
    email = make_email(sender="Weekly <Digest@Quora.com>")
    cond = {"field": "sender", "operator": "contains", "value": "quora.com"}
    assert evaluate(email, cond) is True


def test_contains_no_match():
    email = make_email(sender="someone@example.com")
    cond = {"field": "sender", "operator": "contains", "value": "quora.com"}
    assert evaluate(email, cond) is False


def test_equals_is_case_insensitive_and_exact():
    email = make_email(subject="Invoice")
    assert evaluate(email, {"field": "subject", "operator": "equals", "value": "invoice"})
    assert not evaluate(email, {"field": "subject", "operator": "equals", "value": "inv"})


def test_body_field_is_matched():
    email = make_email(body="Your order has shipped")
    cond = {"field": "body", "operator": "contains", "value": "SHIPPED"}
    assert evaluate(email, cond) is True


def test_missing_text_field_is_treated_as_empty():
    email = make_email()
    email.subject = None
    assert evaluate(email, {"field": "subject", "operator": "equals", "value": ""})
    assert not evaluate(email, {"field": "subject", "operator": "contains", "value": "a"})


def test_unknown_field_never_matches():
    email = make_email(sender="a@b.com")
    assert evaluate(email, {"field": "cc", "operator": "contains", "value": "a"}) is False


def test_date_operator_on_text_field_never_matches():
    email = make_email(sender="a@b.com")
    assert evaluate(email, {"field": "sender", "operator": "before", "value": "1"}) is False


@pytest.mark.parametrize(
    ("operator", "days_old", "limit", "expected"),
    [
        # "before" is true when the email arrived less than `limit` days ago.
        ("before", 2, "7", True),
        ("before", 10, "7", False),
        # "after" is true when the email arrived more than `limit` days ago.
        ("after", 10, "7", True),
        ("after", 2, "7", False),
    ],
)
def test_date_conditions(operator, days_old, limit, expected):
    email = make_email(days_old=days_old)
    cond = {"field": operator, "operator": operator, "value": limit}
    assert evaluate(email, cond) is expected
