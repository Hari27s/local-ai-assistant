import json

REQUIRED_KEYS = {"topic", "definition", "example"}


def validate_response(raw_response):
    try:
        answer = json.loads(raw_response)
    except (json.JSONDecodeError, TypeError):
        return False, "Invalid JSON"

    if not isinstance(answer, dict):
        return False, "Response must be a JSON object"

    if set(answer.keys()) != REQUIRED_KEYS:
        return False, "Missing or extra fields"

    if not all(isinstance(answer[key], str) for key in REQUIRED_KEYS):
        return False, "Invalid field type"

    if not all(answer[key].strip() for key in REQUIRED_KEYS):
        return False, "Empty field"

    return True, "Valid response"


tests = [
    ("Valid JSON", '{"topic":"AI","definition":"Smart systems","example":"Chatbot"}', True),
    ("Invalid JSON", '{"topic":"AI"', False),
    ("Missing field", '{"topic":"AI","definition":"Smart systems"}', False),
    ("Wrong type", '{"topic":"AI","definition":5,"example":"Chatbot"}', False),
    ("Empty field", '{"topic":"","definition":"Smart systems","example":"Chatbot"}', False),
    ("Extra field", '{"topic":"AI","definition":"Smart systems","example":"Chatbot","extra":"x"}', False),
]

passed = 0

for name, raw, expected in tests:
    valid, message = validate_response(raw)
    success = valid == expected

    if success:
        passed += 1

    print(f"{'PASS' if success else 'FAIL'}: {name} - {message}")

print(f"\nResult: {passed}/{len(tests)} tests passed")