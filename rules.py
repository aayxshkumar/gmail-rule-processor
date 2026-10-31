import json
from datetime import datetime, timedelta

VALID_OPERATORS = {'contains', 'equals', 'before', 'after'}


def load_rules(path='rules.json'):
    with open(path) as f:
        rules = json.load(f)
    if rules.get('predicate') not in {'all', 'any'}:
        raise ValueError('predicate must be "all" or "any"')
    for cond in rules.get('conditions', []):
        if cond.get('operator') not in VALID_OPERATORS:
            raise ValueError(f"Invalid operator: {cond.get('operator')}")
    return rules


def evaluate(e, cond: dict) -> bool:
    """Return whether one rule condition matches an Email row."""
    field, op, val = cond['field'], cond['operator'], cond['value']
    if field == 'sender': target = e.sender or ''
    elif field == 'subject': target = e.subject or ''
    elif field == 'body': target = e.body or ''
    elif field in ('before','after'):
        delta = datetime.now() - e.date_received
        days  = int(val)
        return (delta < timedelta(days=days)) if op=='before' else (delta > timedelta(days=days))
    else:
        return False

    if op == 'contains':    return val.lower() in target.lower()
    if op == 'equals':      return target.lower() == val.lower()
    return False
