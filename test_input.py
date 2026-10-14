def validate_input(question):
    question = question.strip()

    if not question:
        return False, "Question cannot be empty."

    if len(question) > 500:
        return False, "Question is too long. Maximum is 500 characters."

    return True, question


# Test 1: Empty input
valid, result = validate_input("")
print("Test 1 - Empty input:", result)

# Test 2: Normal input
valid, result = validate_input("What is Machine Learning?")
print("Test 2 - Normal input:", result)

# Test 3: Input containing only spaces
valid, result = validate_input("   ")
print("Test 3 - Spaces only:", result)

# Test 4: Overly long input
valid, result = validate_input("A" * 501)
print("Test 4 - Long input:", result)

print("\nInput validation tests complete.")