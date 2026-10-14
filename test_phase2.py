import json
import csv
import requests

MODEL = "llama3.2:1b"
API_URL = "http://localhost:11434/api/generate"

SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "definition": {"type": "string"},
        "example": {"type": "string"}
    },
    "required": ["topic", "definition", "example"],
    "additionalProperties": False
}

PROMPT = """
You are a beginner-friendly study assistant.
Answer in simple English.
Return a JSON object with topic, definition, and example.
Question: What is Machine Learning?
"""

with open("phase2_results.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["run", "valid_json", "has_all_fields", "topic"])

    for run in range(1, 6):
        print(f"Testing run {run}/5...")

        try:
            response = requests.post(
                API_URL,
                json={
                    "model": MODEL,
                    "prompt": PROMPT,
                    "format": SCHEMA,
                    "stream": False,
                    "options": {
                        "temperature": 0,
                        "seed": 42,
                        "num_predict": 120
                    }
                },
                timeout=180
            )
            response.raise_for_status()

            data = response.json()
            answer = json.loads(data["response"])

            required = {"topic", "definition", "example"}
            valid_json = True
            has_all_fields = (
                set(answer.keys()) == required
                and all(isinstance(answer[k], str) for k in required)
            )

            print(json.dumps(answer, indent=2))
            print(f"Valid JSON: {valid_json}")
            print(f"All required fields: {has_all_fields}\n")

            writer.writerow([
                run, valid_json, has_all_fields,
                answer.get("topic", "")
            ])
            file.flush()

        except (requests.RequestException, ValueError, KeyError) as error:
            print(f"Run {run} failed: {error}\n")
            writer.writerow([run, False, False, "ERROR"])
            file.flush()

print("Test complete. Open phase2_results.csv.")