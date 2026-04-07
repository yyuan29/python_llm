from python_llm.chat import Chat

def run_integration_tests():
    print("Running integration tests for Chat...")

    # --- Test 1: basic interaction ---
    chat = Chat()
    user_input = "Hello"
    response = chat.send_message(user_input)
    assert response is not None, "Test 1 failed: response is None"
    assert isinstance(response, str), "Test 1 failed: response is not a string"
    assert len(response) > 0, "Test 1 failed: response is empty"
    print("Test 1 passed: basic interaction")

    # --- Test 2: multiple sequential messages ---
    messages = ["Hi", "How are you?", "Tell me a joke"]
    for i, msg in enumerate(messages, start=2):
        resp = chat.send_message(msg)