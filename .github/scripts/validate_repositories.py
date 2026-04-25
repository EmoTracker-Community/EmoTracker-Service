import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

import jsonschema

REPOS_FILE = "service/package_repositories.json"
SCHEMA_FILE = "sdk/schema/repository.json"
TIMEOUT = 15


def get_base_contents(base_ref):
    result = subprocess.run(
        ["git", "show", f"origin/{base_ref}:{REPOS_FILE}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return {}
    return json.loads(result.stdout)


def main():
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    base_ref = os.environ.get("BASE_REF", "main")

    with open(REPOS_FILE) as f:
        new_repos = json.load(f)

    if event == "pull_request_target":
        old_repos = get_base_contents(base_ref)
        changed = {k: v for k, v in new_repos.items()
                   if k not in old_repos or old_repos[k] != v}
        if not changed:
            print("No repository URLs were added or modified.")
            sys.exit(0)
        print(f"Checking {len(changed)} added/modified repository URL(s)...")
    else:
        changed = new_repos
        print(f"Checking all {len(changed)} repository URL(s)...")

    with open(SCHEMA_FILE) as f:
        schema = json.load(f)

    flag_enum = schema["definitions"]["package"]["properties"]["flags"]["items"]["enum"]
    canonical_flags = {f.lower(): f for f in flag_enum}

    def normalize_flags(data):
        for package in data.get("packages", []):
            if "flags" in package:
                package["flags"] = [canonical_flags.get(f.lower(), f) for f in package["flags"]]
            for variant in package.get("variants", []):
                if "flags" in variant:
                    variant["flags"] = [canonical_flags.get(f.lower(), f) for f in variant["flags"]]

    failed = False
    for name, url in changed.items():
        print(f"\n{name}\n  {url}")
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
                content = resp.read().decode("utf-8")
        except urllib.error.URLError as e:
            print(f"  ✗ Could not fetch: {e.reason}")
            failed = True
            continue
        except Exception as e:
            print(f"  ✗ Could not fetch: {e}")
            failed = True
            continue

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"  ✗ Response is not valid JSON: {e}")
            failed = True
            continue

        normalize_flags(data)

        try:
            jsonschema.validate(instance=data, schema=schema)
            print(f"  ✓ Valid")
        except jsonschema.ValidationError as e:
            print(f"  ✗ Schema violation: {e.message}")
            failed = True

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
