from agentspring.tools import tool_registry

@tool_registry.register("read_csv")
def read_csv(file_path: str) -> dict:
    import pandas as pd
    df = pd.read_csv(file_path)
    return {"data": df.to_dict(orient="records")}

@tool_registry.register("summarize_issues")
def summarize_issues(rows: list) -> dict:
    from collections import Counter
    issues = [row["issue"] for row in rows if "issue" in row]
    common = Counter(issues).most_common(3)
    if not common:
        summary_text = "No issues found."
    else:
        summary_text = "Top issues:\n" + "\n".join(
            f"{i+1}. {issue} (reported {count} times)" for i, (issue, count) in enumerate(common)
        )
    return {"summary": summary_text}

@tool_registry.register("write_summary")
def write_summary(summary: str, file_path: str = "summary.txt") -> dict:
    with open(file_path, "w") as f:
        f.write(summary)
    return {"success": True, "file": file_path}

@tool_registry.register("llm_summarize_issues")
def llm_summarize_issues(issues: list) -> dict:
    """
    Use an LLM to group similar issues and summarize the top 3 most common problems in a human-readable way.
    """
    from agentspring.llm import LLMHelper
    llm = LLMHelper()
    prompt = (
        "Given the following list of customer complaints, group similar issues (even if worded differently) "
        "and summarize the top 3 most common problems people are reporting. "
        "Respond with a short, human-readable summary.\n\nComplaints:\n"
        + "\n".join(f"- {issue}" for issue in issues)
    )
    summary = llm.summarize(prompt, max_length=200)
    return {"summary": summary}
