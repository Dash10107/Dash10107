import json
import os
import re
import sys

def main():
    # Read the event path from GitHub environment
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        print("Error: GITHUB_EVENT_PATH not set.")
        sys.exit(1)

    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)

    # Get user details
    issue = event.get("issue", {})
    user = issue.get("user", {})
    username = user.get("login")
    avatar_url = user.get("avatar_url")
    body = issue.get("body", "")

    if not username or not avatar_url:
        print("Error: Could not retrieve user details from issue event.")
        sys.exit(1)

    # Parse message from YAML issue body
    message = ""
    if "### Message" in body:
        message = body.split("### Message")[1].strip()
    else:
        message = body.strip()

    # Sanitize message to prevent HTML injection and keep it clean
    message = re.sub(r"<[^>]*>", "", message)  # strip any HTML tags
    message = message.replace("\n", " ").replace("\r", "")
    message = message.replace("\"", "&quot;").replace("'", "&#39;")
    
    # Cap message length to prevent layout breaks
    if len(message) > 150:
        message = message[:147] + "..."

    if not message:
        message = "Hi! Visited your profile today."

    # Format the new entry
    new_entry = f"""  <tr>
    <td align="center" width="20%">
      <a href="https://github.com/{username}">
        <img src="{avatar_url}" width="40" height="40" style="border-radius: 50%;" alt="{username}" /><br />
        <sub><b>{username}</b></sub>
      </a>
    </td>
    <td valign="middle">
      {message}
    </td>
  </tr>"""

    # Read README
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        print("Error: README.md not found.")
        sys.exit(1)

    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()

    # Find the guestbook markers
    pattern = r"(<!--\s*START_GUESTBOOK\s*-->)(.*?)(<!--\s*END_GUESTBOOK\s*-->)"
    match = re.search(pattern, readme_content, re.DOTALL)

    if not match:
        print("Error: Guestbook comment markers not found in README.md.")
        sys.exit(1)

    start_tag, guestbook_body, end_tag = match.groups()

    # Parse existing rows
    existing_rows = re.findall(r"<tr>.*?</tr>", guestbook_body, re.DOTALL)
    
    # Prepend new row
    all_rows = [new_entry] + existing_rows
    
    # Keep only the last 10 entries to keep the profile concise
    all_rows = all_rows[:10]

    # Reconstruct the guestbook block
    new_guestbook_body = "\n" + "\n".join(all_rows) + "\n"
    
    # Replace in README
    replacement = f"{start_tag}{new_guestbook_body}{end_tag}"
    new_readme_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)

    # Save README
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme_content)

    print(f"Successfully added guestbook entry for user: {username}")

if __name__ == "__main__":
    main()
