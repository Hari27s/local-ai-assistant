import csv
import time
import json
import requests

MODEL = "llama3.2:1b"
API_URL = "http://localhost:11434/api/generate"

prompts = [
    "What is artificial intelligence? Explain in 3 sentences.",
    "What is a transistor?",
    "Write a Python program to add two numbers."
]

with open("results.csv", "w", newline="", encoding="utf-8") as file:
    columns = [
        "model", "prompt", "run",
        "ttft_ms", "total_latency_ms",
        "output_tokens", "tokens_per_second"
    ]
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()

    for prompt in prompts:
        for run in range(1, 4):
            print(f"\nPrompt: {prompt} | Run: {run}")

            payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": True,
                "options": {"temperature": 0}
            }

            start = time.perf_counter()
            first_output = None
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

                        data = __import__("json").loads(line)
                        chunk = data.get("response", "")

                        if chunk and first_output is None:
                            first_output = time.perf_counter()

                        if data.get("done"):
                            stats = data

                end = time.perf_counter()

                ttft = (
                    (first_output - start) * 1000
                    if first_output else None
                )
                latency = (end - start) * 1000
                tokens = stats.get("eval_count", 0)
                duration = stats.get("eval_duration", 0)
                speed = (
                    tokens / (duration / 1e9)
                    if duration else 0
                )

                writer.writerow({
                    "model": MODEL,
                    "prompt": prompt,
                    "run": run,
                    "ttft_ms": round(ttft, 2) if ttft else "",
                    "total_latency_ms": round(latency, 2),
                    "output_tokens": tokens,
                    "tokens_per_second": round(speed, 2)
                })
                file.flush()

                print(f"TTFT: {ttft:.0f} ms" if ttft else "TTFT unavailable")
                print(f"Total latency: {latency:.0f} ms")
                print(f"Generation speed: {speed:.2f} tokens/sec")

            except requests.RequestException as error:
                print(f"Request failed: {error}")
                print("Check that Ollama is running.")
                break

print("\nBenchmark finished. Check results.csv in your project folder.")