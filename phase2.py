import json
import requests

MODEL = "llama3.2:1b"
API_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = """
You are a beginner-friendly study assistant.
Use simple English.
Give a short definition and one practical example.
Do not invent facts.
If you are unsure, say so.
Return only the requested JSON object.
"""

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

print("=== Phase 2: Structured Local AI Assistant ===")
print("Ask a study question, or type 'exit' to quit.\n")

while True:
    question = input("You: ").strip()

    if question.lower() == "exit":
        print("Goodbye!")
        break

    if not question:
        print("Please enter a question.\n")
        continue

    if len(question) > 500:
        print("Please keep your question under 500 characters.\n")
        continue

    payload = {
        "model": MODEL,
        "prompt": SYSTEM_PROMPT + "\nQuestion: " + question,
        "format": SCHEMA,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 150}
    }

    try:
       response = requests.post( 
               API_URL, json=payload, timeout=180
        )
       response.raise_for_status()

       result = response.json()
       answer = json.loads(result["response"])

       required_keys = {"topic", "definition", "example"}

       if not isinstance(answer, dict):
            print("The response must be a JSON object.\n")
            continue

       if set(answer.keys()) != required_keys:
            print("The response did not match the required fields.\n")
            continue

       if not all(isinstance(answer[key], str)
                   for key in required_keys):
            print("The response contains an invalid field type.\n")
            continue
       if not all(answer[key].strip() 
                   for key in required_keys):
            print("The response contains an empty field.\n")
            continue

       print("\n--- Structured Answer ---")
       print(json.dumps(answer, indent=2, ensure_ascii=False))
       print("\n--- Performance ---")

       if result.get("eval_duration"):
            speed = (
                result["eval_count"] /
                (result["eval_duration"] / 1e9)
            )
            print(f"Generation speed: {speed:.2f} tokens/sec")

       print(
            f"Total latency: "
            f"{result.get('total_duration', 0) / 1e6:.0f} ms"
        )
       print()

    except requests.RequestException as error:
        print(f"\nConnection error: {error}\n")
    except (ValueError, KeyError) as error:
        print(f"\nCould not validate the AI response: {error}\n")