import os
import json
import subprocess
import re
import urllib.request
import urllib.error
import google.generativeai as genai

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

    print(f"Analyzing Repository: {repo_name}")
    print(f"Issue #{issue_number}: {issue_title}")

    # 3. Configure Gemini
    genai.configure(api_key=gemini_api_key)
    # Using Gemini 1.5 Pro to handle potentially massive codebase context windows
    model = genai.GenerativeModel('gemini-1.5-pro') 

    # 4. Construct the Prompt
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

    # 5. Call Gemini API
    print("Generating solution via Gemini...")
    response = model.generate_content(system_prompt)
    
    # Clean the response to ensure we only parse JSON
    response_text = response.text
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
    for mod in modifications:
        file_path = mod.get("file_path")
        new_content = mod.get("new_content")
        if not file_path or new_content is None:
            print(f"Skipping invalid modification entry: {mod}")
            continue

        parent = os.path.dirname(file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated: {file_path}")

    # Keep this step non-destructive by default.
    subprocess.run(["git", "status", "--short"], check=False)
    print("Agent completed local file updates.")

if __name__ == "__main__":
    main()
