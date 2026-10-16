Local AI Assistant 🤖

A lightweight, locally running AI assistant built with Python and Ollama. This project explores local language models, streaming responses, conversation memory, and performance benchmarking.

🚀 Features

- Local AI inference: Run language models locally using Ollama.
- Streaming responses: Display answers as they are generated.
- Conversation memory: Maintain conversational context during a session.
- Persistent memory: Phase 5 experiments with saving conversation history to a local JSON file.
- Performance metrics: Measure time to first token (TTFT), total response latency, generation speed, output tokens, and prompt tokens.
- Model benchmarking: Compare local language models using repeatable test questions.

🛠️ Tech Stack

- Python
- Ollama
- Requests
- JSON
- Git and GitHub

🧠 Models Tested

Model| Average TTFT| Average Latency| Average Speed
Llama 3.2 1B| 2395.23 ms| 12285.2 ms| 11.17 tokens/sec
Qwen 2.5 1.5B| 2832.36 ms| 8522.79 ms| 12.73 tokens/sec

Benchmark summary: In the recorded tests, Qwen 2.5 1.5B had lower average response latency and higher generation speed, while Llama 3.2 1B had lower time to first token.

Results are from nine tests per model on the original test setup. Performance varies with hardware, prompts, and system conditions.

📂 Project Structure

- "main.py" — Original assistant program
- "phase2.py" — Input handling and validation
- "phase4.py" — Streaming assistant with conversation history and performance metrics
- "phase5.py" — Persistent conversation-memory experiment
- "benchmark.py" — Benchmarking utilities
- "compare_models.py" — Model comparison
- "phase2_results.csv" — Phase 2 results
- "phase3_results.csv" — Phase 3 benchmark results

Additional test and support files are included in the repository.

⚙️ Requirements

- Python 3
- Ollama
- A locally installed Ollama model
- Python package: "requests"

🏁 Getting Started

1. Install Ollama

Download Ollama from https://ollama.com/.

2. Download a model

Open a terminal and run:

ollama pull llama3.2:1b

3. Clone this repository

git clone https://github.com/Hari27s/local-ai-assistant.git
cd local-ai-assistant

Replace "Hari27s" with your GitHub username.

4. Create and activate a virtual environment

On Windows PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

5. Install dependencies

pip install requests

6. Run the assistant

python phase4.py

To try the persistent-memory version:

python phase5.py

Type "exit" to quit the assistant.

📊 Performance Metrics

The assistant measures:

- TTFT: Time taken to receive the first generated token.
- Total latency: Time taken to complete a response.
- Generation speed: Generated tokens per second.
- Output tokens: Number of tokens generated.
- Prompt tokens: Number of tokens processed from the input context.

🔮 Future Improvements

- Improve long-term memory and reliable fact recall.
- Add automated benchmark reports and visualizations.
- Evaluate more local language models.
- Improve error handling and response validation.

👨‍💻 About

This project is a hands-on exploration of local AI systems, Python development, LLM performance evaluation, and conversational memory.

Built as a learning project to understand how local AI assistants work.
