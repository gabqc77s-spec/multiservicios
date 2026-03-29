import json
import os

def test_robust_json_extraction():
    # Mocking the extraction logic from src/agent.py
    def extract_json(response_text):
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_block = response_text[start_idx:end_idx+1]
            return json.loads(json_block)
        return None

    # Case 1: Pure JSON
    res1 = '{"file.py": "print(1)"}'
    assert extract_json(res1) == {"file.py": "print(1)"}

    # Case 2: Markdown block
    res2 = 'Here is the code:\n```json\n{"file.py": "print(1)"}\n```'
    assert extract_json(res2) == {"file.py": "print(1)"}

    # Case 3: Nested braces in content
    res3 = 'Extra text {"file.py": "if True: { print(1) }" } more text'
    assert extract_json(res3) == {"file.py": "if True: { print(1) }"}

    # Case 4: No JSON
    res4 = 'Hello world'
    assert extract_json(res4) is None

    print("Robust JSON extraction tests passed!")

if __name__ == "__main__":
    test_robust_json_extraction()
