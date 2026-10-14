import json
import time
import requests

MODEL = "llama3.2:1b"
API_URL = "http://localhost:11434/api/generate"

print("=== My Local AI Assistant ===")
print("Type 'exit' to quit.\n")

while True:
    question = input("You: ").strip()

    if question.lower() == "exit":
        print("Goodbye!")
        break

    if not question:
        continue

    payload = {
        "model": MODEL,
        "prompt": question,
        "stream": True,
        "options": {"temperature": 0}
    }

    start = time.perf_counter()
    first_output_time = None
    stats = {}

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
                chunk = data.get("response", "")

                if chunk and first_output_time is None:
                    first_output_time = time.perf_counter()

                print(chunk, end="", flush=True)

                if data.get("done"):
                    stats = data

        end = time.perf_counter()

        print("\n\n--- Performance Results ---")

        if first_output_time is not None:
            ttft = (first_output_time - start) * 1000
            print(f"Time to first output: {ttft:.0f} ms")

        latency = (end - start) * 1000
        print(f"Total response latency: {latency:.0f} ms")

        output_tokens = stats.get("eval_count", 0)
        generation_time = stats.get("eval_duration", 0)

        if generation_time > 0:
            speed = output_tokens / (generation_time / 1e9)
            print(f"Generation speed: {speed:.2f} tokens/sec")

        print(f"Output tokens: {output_tokens}")
        print(f"Prompt tokens: {stats.get('prompt_eval_count', 0)}")
        print()

    except requests.RequestException as error:
        print(f"\nConnection error: {error}")
        print("Check that Ollama is running.")

    except json.JSONDecodeError:
        print("\nCould not read the response. Please try again.")