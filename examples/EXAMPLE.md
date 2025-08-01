# AgentSpring Full Stack Example: LLM-Powered Complaint Summarization

## Overview
This example demonstrates how to use AgentSpring for agentic, LLM-powered orchestration to analyze customer complaints and produce a high-level summary of the top issues. It showcases:
- **Agentic orchestration**: Natural language instructions are interpreted and executed as a sequence of tool invocations.
- **LLM-powered summarization**: An LLM groups and summarizes similar complaints, even if worded differently.
- **Extensible tool registry**: Easily add or swap tools for new data sources or output formats.

## What This Example Does
- Reads a CSV file (`complaints.csv`) containing customer complaints.
- Passes all complaint texts to an LLM, which groups and summarizes the top 3 most common problems.
- Writes the summary to a file (`summary.txt`).

**Use Case:**
> Automatically extract the main pain points from large volumes of customer feedback, support tickets, or survey responses, even when users describe the same problem in different words.

## Why Agentic Orchestration?
Traditional (non-agentic) solutions require you to hardcode the pipeline, making it brittle and inflexible:
- You must specify every step and data dependency in advance.
- If you want to change the workflow, add a new tool, or support a new data source, you must rewrite the pipeline.
- Classic summarizers only count exact string matches, failing to group semantically similar complaints.

**Agentic (LLM-powered) Solution:**
- Accepts natural language instructions and dynamically generates the right sequence of tool invocations.
- Can adapt to new tools or data formats with minimal changes.
- Uses an LLM to semantically group and summarize similar complaints, providing more accurate and actionable insights.

## How to Run the Example

### 1. Prerequisites
- Python 3.8+
- [Ollama](https://ollama.com/) LLM server running locally (default: `http://localhost:11434`)
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Prepare Your Data
- Place a file named `complaints.csv` in the project root. It should have at least an `issue` column with free-text complaints.

### 3. Start the LLM Server (Ollama)
Before running the example, make sure the Ollama server is running locally:
```bash
ollama serve
```
This will start Ollama on `http://localhost:11434` by default. Leave this terminal open while running the example.

### 4. Configure the LLM Endpoint (Optional)
By default, the example connects to Ollama at `http://localhost:11434`.
- To use a custom endpoint, set the environment variable:
  ```bash
  export OLLAMA_BASE_URL=http://host.docker.internal:11434
  ```
- Or pass a custom `base_url` to the `LLMHelper` in your code.

### 5. Run the Example
```bash
PYTHONPATH=. python agentspring/full_stack_example.py
```

### 6. Output
- The script prints the CSV contents, step-by-step execution, and the LLM-generated summary.
- The summary is saved to `summary.txt`.

## FAQ & Troubleshooting

**Q: I get a connection error to Ollama or LLM.**
- Make sure Ollama is running: `curl http://localhost:11434`
- If running in Docker, use `host.docker.internal` as the host.
- Check the `OLLAMA_BASE_URL` environment variable.

**Q: The summary just repeats the first three complaints.**
- This happens if you use the basic Python summarizer. Switch to the LLM-powered summarizer for semantic grouping.

**Q: The script can't find `complaints.csv`.**
- Ensure the file is in the project root, not inside a subdirectory.

**Q: How do I add new tools or change the workflow?**
- Register a new tool in any file within `agentspring/tools/`.
- Update the pipeline in `full_stack_example.py` or use agentic orchestration for dynamic plans.

## Example Comparison: Agentic vs. Non-Agentic

| Feature                        | Non-Agentic Pipeline        | Agentic (LLM) Pipeline           |
|--------------------------------|-----------------------------|----------------------------------|
| Workflow Adaptability          | Hardcoded, inflexible       | Dynamic, adapts to new tools     |
| Handles Similar Complaints     | No (exact matches only)     | Yes (semantic grouping via LLM)  |
| Natural Language Instructions  | No                          | Yes                              |
| Adds/Removes Steps Easily      | Manual code changes         | LLM/plan adapts automatically    |
| Human-Readable Summaries       | Basic (counts/keywords)     | Yes, LLM-generated               |

## Example Use Cases
- Customer support analytics
- Product feedback mining
- Survey result summarization
- Automated helpdesk triage

## Contact & Support
For further help or to extend this example, see the main AgentSpring documentation or open an issue.
