import os
import json
import subprocess
import re
from datetime import datetime, timezone
import urllib.request
import urllib.error
from google import genai

def github_api(method, endpoint, token, data=None):
    """Helper function to make GitHub API calls without third-party libraries."""
    url = f"https://api.github.com{endpoint}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Gemini-Auto-Agent"
    }
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"GitHub API Error: {e.code} - {e.read().decode('utf-8')}")
        raise

def get_codebase_context():
    """Reads all relevant text files in the repository to build context."""
    code_context = ""
    for root, dirs, files in os.walk("."):
        # Exclude version control, caches, and build directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.github', 'node_modules', 'venv', 'dist', 'build']]
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    code_context += f"\n--- {filepath} ---\n{content}\n"
            except Exception:
                # Silently skip binary files or unreadable formats
                pass 
    return code_context

def extract_response_text(response):
    """Extract text from google.genai responses with graceful fallbacks."""
    text = getattr(response, "text", None)
    if text:
        return text

    candidates = getattr(response, "candidates", None) or []
    parts_text = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            part_text = getattr(part, "text", None)
            if part_text:
                parts_text.append(part_text)
    return "\n".join(parts_text).strip()

def generate_with_fallback(api_key, prompt):
    """Try a sequence of Gemini models and return the first successful response text."""
    client = genai.Client(api_key=api_key)
    requested_model = os.environ.get("GEMINI_MODEL", "").strip()

    model_candidates = []
    if requested_model:
        model_candidates.append(requested_model)
    model_candidates.extend([
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
    ])

    attempted = set()
    errors = []
    for model_name in model_candidates:
        if not model_name or model_name in attempted:
            continue
        attempted.add(model_name)
        try:
            print(f"Trying Gemini model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            response_text = extract_response_text(response)
            if not response_text:
                raise RuntimeError("Empty response text.")
            return response_text, model_name
        except Exception as e:
            errors.append(f"{model_name}: {e}")
            print(f"Model failed: {model_name} -> {e}")

    # Best-effort model listing for easier troubleshooting
    try:
        available = []
        for model in client.models.list():
            name = getattr(model, "name", "")
            if name:
                available.append(name)
            if len(available) >= 25:
                break
        if available:
            print("Available models (first 25):")
            for name in available:
                print(f"- {name}")
    except Exception as list_error:
        print(f"Could not list models: {list_error}")

    raise RuntimeError("All model attempts failed: " + " | ".join(errors))

def run_cmd(args, check=True):
    """Run a subprocess command and print stdout/stderr for action logs."""
    print("+ " + " ".join(args))
    result = subprocess.run(args, check=check, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    return result

def normalize_relative_path(file_path):
    """Normalize and validate model-provided file path stays inside workspace."""
    if not isinstance(file_path, str) or not file_path.strip():
        return None
    normalized = os.path.normpath(file_path).lstrip("/\\")
    if normalized in (".", "") or normalized.startswith(".."):
        return None
    return normalized

def main():
    # 1. Load the only two required secrets
    github_token = os.environ.get("GITHUB_TOKEN")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if not github_token or not gemini_api_key:
        print("Error: GITHUB_TOKEN and GEMINI_API_KEY must be set.")
        exit(1)

    # 2. Extract context dynamically from the native GitHub Action event payload
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        print("Error: GITHUB_EVENT_PATH not found. Are you running this in GitHub Actions?")
        exit(1)

    with open(event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)

    issue = event_data.get("issue", {})
    repo = event_data.get("repository", {})
    
    issue_number = issue.get("number")
    issue_title = issue.get("title")
    issue_body = issue.get("body") or "No description provided."
    repo_name = repo.get("full_name")
    default_branch = repo.get("default_branch", "main")

    if not repo_name or not issue_number:
        print("Error: Missing repository or issue information in event payload.")
        exit(1)

    print(f"Analyzing Repository: {repo_name}")
    print(f"Issue #{issue_number}: {issue_title}")

    # 3. Construct the Prompt
    system_prompt = f"""
    You are an expert autonomous software engineer resolving a GitHub issue.

    Issue Title: {issue_title}
    Issue Body: {issue_body}

    Below is the current codebase context:
    {get_codebase_context()}

    Analyze the issue and the codebase. Provide the exact code changes required to resolve the issue.

    Output strictly a valid JSON object matching the following schema, and absolutely no other text, markdown formatting, or explanations:
    {{
        "modifications": [
            {{
                "file_path": "path/to/existing_or_new_file.py",
                "new_content": "the complete new content of the file (do not use diffs, output the entire updated file)"
            }}
        ],
        "commit_message": "Descriptive commit message",
        "pr_title": "Title for the Pull Request",
        "pr_body": "Description of the changes made."
    }}
    """

    # 4. Call Gemini API
    print("Generating solution via Gemini...")
    response_text, model_used = generate_with_fallback(gemini_api_key, system_prompt)
    print(f"Gemini response received from model: {model_used}")
    
    # Clean the response to ensure we only parse JSON
    json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if not json_match:
        print("Error: Gemini response did not contain a JSON object.")
        print("Raw response:")
        print(response_text)
        exit(1)

    try:
        result = json.loads(json_match.group(0))
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse Gemini JSON output: {e}")
        print("Raw response:")
        print(response_text)
        exit(1)

    modifications = result.get("modifications", [])
    if not isinstance(modifications, list):
        print("Error: 'modifications' must be a list.")
        exit(1)

    print(f"Applying {len(modifications)} file modification(s)...")
    touched_files = []
    for mod in modifications:
        file_path = mod.get("file_path")
        new_content = mod.get("new_content")
        if not file_path or new_content is None:
            print(f"Skipping invalid modification entry: {mod}")
            continue

        normalized_path = normalize_relative_path(file_path)
        if not normalized_path:
            print(f"Skipping unsafe path: {file_path}")
            continue

        parent = os.path.dirname(normalized_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(normalized_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        touched_files.append(normalized_path)
        print(f"Updated: {normalized_path}")

    status = run_cmd(["git", "status", "--short"], check=False)
    if not status.stdout.strip():
        print("No file changes detected; skipping commit and PR.")
        github_api(
            "POST",
            f"/repos/{repo_name}/issues/{issue_number}/comments",
            github_token,
            {"body": "Gemini agent ran, but no file changes were generated."},
        )
        return

    commit_message = (result.get("commit_message") or f"Resolve issue #{issue_number}").strip()
    pr_title = (result.get("pr_title") or f"Resolve issue #{issue_number}: {issue_title}").strip()
    pr_body = (result.get("pr_body") or "Automated changes generated by Gemini agent.").strip()
    if f"Closes #{issue_number}" not in pr_body:
        pr_body = f"{pr_body}\n\nCloses #{issue_number}"

    branch_suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    branch_name = f"gemini/issue-{issue_number}-{branch_suffix}"

    run_cmd(["git", "config", "user.name", "gemini-auto-agent"])
    run_cmd(["git", "config", "user.email", "gemini-auto-agent@users.noreply.github.com"])
    run_cmd(["git", "checkout", "-b", branch_name])
    run_cmd(["git", "add", "-A"])

    commit_result = run_cmd(["git", "commit", "-m", commit_message], check=False)
    if commit_result.returncode != 0:
        print("No commit created; skipping push and PR.")
        return

    run_cmd(["git", "push", "--set-upstream", "origin", branch_name])

    pr_payload = {
        "title": pr_title,
        "head": branch_name,
        "base": default_branch,
        "body": pr_body,
    }
    pr_response = github_api("POST", f"/repos/{repo_name}/pulls", github_token, pr_payload)
    pr_url = pr_response.get("html_url")
    print(f"Created PR: {pr_url}")

    comment_body = (
        f"Created PR: {pr_url}\n\n"
        f"Branch: `{branch_name}`\n"
        f"Files changed: {len(touched_files)}"
    )
    github_api(
        "POST",
        f"/repos/{repo_name}/issues/{issue_number}/comments",
        github_token,
        {"body": comment_body},
    )
    print("Agent completed: branch pushed and PR opened.")

if __name__ == "__main__":
    main()
