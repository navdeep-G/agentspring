from agentspring.tools import tool_registry
import pandas as pd

@tool_registry.register("read_csv", "Read file and return as pandas DataFrame")
def read_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df

@tool_registry.register("print_csv_head", "Return the first 5 rows of a pandas DataFrame")
def print_csv_head(df: pd.DataFrame) -> pd.DataFrame:
   return df.head()

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
def llm_summarize_issues(data: list) -> dict:
    from agentspring.llm import LLMHelper
    issues = [row["issue"] for row in data if "issue" in row]
    if not issues:
        return {"summary": "No issues found."}
    prompt = (
        "Given the following list of customer complaints, group similar issues (even if worded differently) "
        "and summarize the top 3 most common problems people are reporting. "
        "Respond with a short, human-readable summary.\n\nComplaints:\n"
        + "\n".join(f"- {issue}" for issue in issues)
    )
    llm = LLMHelper()
    summary = llm.summarize(prompt, max_length=200)
    return {"summary": summary}

