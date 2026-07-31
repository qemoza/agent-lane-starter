"""GitHub Issues adapter. The lane is a label.

Good first choice if the work is code: the agent already has the repo in front of it.

.env needs:
    BOARD=github
    GITHUB_TOKEN=REPLACE_ME           a token with repo access
    GITHUB_REPO=REPLACE_ME/REPLACE_ME owner/name
    GITHUB_AGENT_LABEL=agent
    GITHUB_REVIEW_LABEL=review
"""
import os

import requests

API = "https://api.github.com"


def _headers():
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set in .env")
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}


def fetch_agent_tasks():
    repo = os.environ["GITHUB_REPO"]
    label = os.environ.get("GITHUB_AGENT_LABEL", "agent")
    r = requests.get(
        f"{API}/repos/{repo}/issues",
        headers=_headers(),
        params={"labels": label, "state": "open", "per_page": 50},
        timeout=30,
    )
    r.raise_for_status()
    # The issues endpoint also returns pull requests. Those are not tasks.
    return [{
        "id": str(i["number"]),
        "title": i.get("title", ""),
        "description": i.get("body") or "",
        "definition_of_done": "",
    } for i in r.json() if "pull_request" not in i]


def post_result(task, text):
    repo = os.environ["GITHUB_REPO"]
    r = requests.post(
        f"{API}/repos/{repo}/issues/{task['id']}/comments",
        headers=_headers(),
        json={"body": text},
        timeout=30,
    )
    r.raise_for_status()


def move_to_review(task):
    repo = os.environ["GITHUB_REPO"]
    agent = os.environ.get("GITHUB_AGENT_LABEL", "agent")
    review = os.environ.get("GITHUB_REVIEW_LABEL", "review")
    requests.post(
        f"{API}/repos/{repo}/issues/{task['id']}/labels",
        headers=_headers(), json={"labels": [review]}, timeout=30,
    ).raise_for_status()
    # Drop the agent label last. If this call fails the task is labelled twice, which
    # you can see. The other order would silently re-run it every poll.
    requests.delete(
        f"{API}/repos/{repo}/issues/{task['id']}/labels/{agent}",
        headers=_headers(), timeout=30,
    )
