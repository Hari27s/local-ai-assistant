import csv
import json
import time
import requests

API_URL = "http://localhost:11434/api/generate"

MODELS = [
    "llama3.2:1b",
    "qwen2.5:1.5b",
]

PROMPTS = [
    "What is artificial intelligence? Explain in 3 sentences.",
    "What is a transistor? Explain simply.",
    "Write a Python program to add two numbers.",
]

RUNS = 3
MAX_TOKENS = 120
OUTPUT_FILE = "phase3_results.csv"


def generate(model, prompt):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0,
            "seed": 42,
            "num_predict": MAX_TOKENS,
        },
        "keep_alive": "2m",
    }

    start = time.perf_counter()
    first_output = None
    answer_parts = []
    stats = {}

    with requests.post(
        API_URL,
        json=payload,
        stream=True,
        timeout=(10, 300),
    ) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue

            data = json.loads(line)
            chunk = data.get("response", "")

            if chunk:
                if first_output is None:
                    first_output = time.perf_counter()
                answer_parts.append(chunk)

            if data.get("done"):
                stats = data

    end = time.perf_counter()

    eval_count = stats.get("eval_count", 0)
    eval_duration = stats.get("eval_duration", 0)

    return {
        "ttft_ms": round(
            (first_output - start) * 1000, 2
        ) if first_output else "",
        "total_latency_ms": round(
            (end - start) * 1000, 2
        ),
        "load_ms": round(
            stats.get("load_duration", 0) / 1e6, 2
        ),
        "output_tokens": eval_count,
        "tokens_per_second": round(
            eval_count / (eval_duration / 1e9), 2
        ) if eval_duration else 0,
        "answer": "".join(answer_parts),
    }


columns = [
    "model",
    "prompt",
    "run",
    "ttft_ms",
    "total_latency_ms",
    "load_ms",
    "output_tokens",
    "tokens_per_second",
]

print("PHASE 3: TWO-MODEL BENCHMARK")
print("Existing project files will be preserved.")
print("Results will be saved to", OUTPUT_FILE)

try:
    with open(
        OUTPUT_FILE, "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

        for model in MODELS:
            print(f"\n=== Model: {model} ===")
            print("Warm-up request...")

            warmup = generate(
                model,
                "Reply with one short sentence: What is AI?"
            )
            print("Warm-up complete.")

            for prompt in PROMPTS:
                for run in range(1, RUNS + 1):
                    print(
                        f"\n{model} | Question: {prompt} "
                        f"| Run {run}/{RUNS}"
                    )

                    result = generate(model, prompt)

                    writer.writerow({
                        "model": model,
                        "prompt": prompt,
                        "run": run,
                        "ttft_ms": result["ttft_ms"],
                        "total_latency_ms":
                            result["total_latency_ms"],
                        "load_ms": result["load_ms"],
                        "output_tokens": result["output_tokens"],
                        "tokens_per_second":
                            result["tokens_per_second"],
                    })
                    file.flush()

                    print("Answer:", result["answer"][:300])
                    print("TTFT:", result["ttft_ms"], "ms")
                    print(
                        "Total latency:",
                        result["total_latency_ms"], "ms"
                    )
                    print("Model load:", result["load_ms"], "ms")
                    print(
                        "Generation speed:",
                        result["tokens_per_second"], "tokens/sec"
                    )

            # Release this model before loading the next one.
            requests.post(
                API_URL,
                json={
                    "model": model,
                    "prompt": "",
                    "keep_alive": 0,
                },
                timeout=30,
            ).raise_for_status()

    print("\nBenchmark complete!")
    print("Open", OUTPUT_FILE, "to review your results.")

except (requests.RequestException, json.JSONDecodeError) as error:
    print("\nBenchmark request failed:", error)
    print("Check Ollama and the exact model names with ollama list.")
    print("Any completed measurements remain in the CSV.")