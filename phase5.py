import json
import time
import requests
from pathlib import Path

MODEL = "llama3.2:1b"
API_URL = "http://localhost:11434/api/chat"

MEMORY_FILE = Path(__file__).resolve().parent /"memory.json"
print("Memory file:",MEMORY_FILE)
MAX_HISTORY_MESSAGES = 10

try:
    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        conversation_history = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    conversation_history = []
print("Loaded messages:",
      len(conversation_history))
conversation_history = []
MAX_HISTORY_MESSAGES = 20

print("=== Phase 4: Local AI Assistant ===")
print("Type 'exit' to quit.\n")

while True:
    question = input("You: ").strip()

    if question.lower() == "exit":
        print("Goodbye!")
        break

    if not question:
        continue

    conversation_history.append({
        "role": "user",
        "content": question
    })
    payload = {
        "model": MODEL,
        "messages": conversation_history,
        "stream": True,
        "options": {"temperature": 0}
    }

    start = time.perf_counter()
    first_output_time = None
    stats = {}
    answer_parts = []

    try:
        with requests.post(
            API_URL,
            json=payload,
            stream=True,
            timeout=300
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                data = json.loads(line)
                message = data.get("message", {})
                chunk = message.get("content", "")

                if chunk:
                    if first_output_time is None:
                        first_output_time = time.perf_counter()

                    answer_parts.append(chunk)
                    print(chunk, end="", flush=True)

                if data.get("done"):
                    stats = data

        end = time.perf_counter()
        answer = "".join(answer_parts)

        print("\n\n--- Performance Results ---")

        if first_output_time is not None:
            ttft = (first_output_time - start) * 1000
            print(f"Time to first output: {ttft:.0f} ms")
        else:
            print("Time to first output: N/A")

        latency = (end - start) * 1000
        print(f"Total response latency: {latency:.0f} ms")

        output_tokens = stats.get("eval_count", 0)
        generation_time = stats.get("eval_duration", 0)
        prompt_tokens = stats.get("prompt_eval_count", 0)

        if generation_time > 0:
            speed = output_tokens / (generation_time / 1e9)
            print(f"Generation speed: {speed:.2f} tokens/sec")
        else:
            print("Generation speed: N/A")

        print(f"Output tokens: {output_tokens}")
        print(f"Prompt tokens: {prompt_tokens}")
        print()

        if answer:
            
            conversation_history.append({
                "role": "assistant",
                "content": answer
})
            try:
               with open(MEMORY_FILE, "w", encoding="utf-8") as file:
                json.dump(conversation_history, file, indent=2)
            except OSError as error:
              print(f"Could not save memory: {error}")
        if len(conversation_history) > MAX_HISTORY_MESSAGES:
            conversation_history = conversation_history[-MAX_HISTORY_MESSAGES:]
        print("History messages :",len(conversation_history))
    except requests.RequestException as error:
        print(f"\nConnection error: {error}")
        print("Check that Ollama is running.\n")

    except (json.JSONDecodeError, ValueError) as error:
        print(f"\nCould not read the response: {error}\n")