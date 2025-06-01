import json

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