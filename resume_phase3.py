import csv
import time
import json
import requests
from pathlib import Path

API_URL = "http://localhost:11434/api/generate"
RESULTS = Path("phase3_results.csv")

MODELS = ["llama3.2:1b", "qwen2.5:1.5b"]
PROMPTS = [
    "What is artificial intelligence? Explain in 3 sentences.",
    "What is a transistor? Explain simply.",
    "Write a Python program to add two numbers.",
]
RUNS = 3
MAX_TOKENS = 120

COLUMNS = [
    "model", "prompt", "run", "ttft_ms",
    "total_latency_ms", "load_ms",
    "output_tokens", "tokens_per_second",
]


def get_key(row):
    return (row["model"], row["prompt"], row["run"])


if not RESULTS.exists():
    raise SystemExit(
        "phase3_results.csv not found. "
        "Put this script in your project folder."
    )

# Read the existing CSV without modifying it.
with RESULTS.open("r", newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    if not reader.fieldnames or not set(COLUMNS).issubset(reader.fieldnames):
        raise SystemExit(
            "CSV columns do not match the expected Phase 3 format. "
            "No changes were made."
        )
    existing_rows = list(reader)

completed = {
    get_key(row)
    for row in existing_rows
    if all(row.get(k) for k in ("model", "prompt", "run"))
}

print("Existing recorded tests:", len(completed))
print("Expected measured tests:", len(MODELS) * len(PROMPTS) * RUNS)

# Append missing rows only; never write a new header.
with RESULTS.open("a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)

    for model in MODELS:
        for prompt in PROMPTS:
            for run in range(1, RUNS + 1):
                key = (model, prompt, str(run))

                if key in completed:
                    print("Skipping existing:", model, "run", run, prompt)
                    continue

                print(f"\nRunning: {model} | run {run} | {prompt}")

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
                stats = {}

                try:
                    with requests.post(
                        API_URL, json=payload, stream=True,
                        timeout=(10, 300)
                    ) as response:
                        response.raise_for_status()

                        for line in response.iter_lines():
                            if not line:
                                continue
                            data = json.loads(line)
                            if data.get("response") and first_output is None:
                                first_output = time.perf_counter()
                            if data.get("done"):
                                stats = data

                    end = time.perf_counter()
                    tokens = stats.get("eval_count", 0)
                    duration = stats.get("eval_duration", 0)

                    row = {
                        "model": model,
                        "prompt": prompt,
                        "run": run,
                        "ttft_ms": round((first_output - start) * 1000, 2)
                            if first_output else "",
                        "total_latency_ms": round((end - start) * 1000, 2),
                        "load_ms": round(
                            stats.get("load_duration", 0) / 1e6, 2
                        ),
                        "output_tokens": tokens,
                        "tokens_per_second": round(
                            tokens / (duration / 1e9), 2
                        ) if duration else 0,
                    }

                    writer.writerow(row)
                    f.flush()
                    completed.add(key)
                    print("Saved:", row)

                except (requests.RequestException, json.JSONDecodeError) as error:
                    print("Test failed:", error)
                    print("Completed rows are preserved. Run this script again to resume.")
                    raise SystemExit(1)

print("\nResume complete!")
print("Total recorded tests:", len(completed))
print("Results file:", RESULTS)