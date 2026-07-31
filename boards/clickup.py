"""ClickUp adapter. The lane is a status.

.env needs:
    BOARD=clickup
    CLICKUP_TOKEN=REPLACE_ME          Settings → Apps → API token (starts with pk_)
    CLICKUP_LIST_ID=REPLACE_ME        the number in the URL when the list is open
    CLICKUP_AGENT_STATUS=agent        the lane the agent watches
    CLICKUP_REVIEW_STATUS=review      where finished work lands
"""
import os

import requests

API = "https://api.clickup.com/api/v2"


def _headers():
    token = os.environ.get("CLICKUP_TOKEN", "")
    if not token:
        raise RuntimeError("CLICKUP_TOKEN is not set in .env")
    return {"Authorization": token, "Content-Type": "application/json"}


def fetch_agent_tasks():
    list_id = os.environ["CLICKUP_LIST_ID"]
    status = os.environ.get("CLICKUP_AGENT_STATUS", "agent")
    r = requests.get(
        f"{API}/list/{list_id}/task",
        headers=_headers(),
        params={"statuses[]": status, "include_closed": "false"},
        timeout=30,
    )
    r.raise_for_status()
    out = []
    for t in r.json().get("tasks", []):
        # ClickUp custom fields are a list, not a dict. Pull "definition of done" if
        # you made one; the loop works fine without it.
        dod = ""
        for f in t.get("custom_fields") or []:
            if f.get("name", "").strip().lower() in ("definition of done", "done means"):
                dod = f.get("value") or ""
        out.append({
            "id": t["id"],
            "title": t.get("name", ""),
            "description": t.get("description") or t.get("text_content") or "",
            "definition_of_done": dod,
        })
    return out


def post_result(task, text):
    r = requests.post(
        f"{API}/task/{task['id']}/comment",
        headers=_headers(),
        json={"comment_text": text, "notify_all": False},
        timeout=30,
    )
    r.raise_for_status()


def move_to_review(task):
    r = requests.put(
        f"{API}/task/{task['id']}",
        headers=_headers(),
        json={"status": os.environ.get("CLICKUP_REVIEW_STATUS", "review")},
        timeout=30,
    )
    r.raise_for_status()
