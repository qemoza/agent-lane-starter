"""Trello adapter. The lane is a list.

.env needs:
    BOARD=trello
    TRELLO_KEY=REPLACE_ME             trello.com/power-ups/admin → API key
    TRELLO_TOKEN=REPLACE_ME           generated from that same page
    TRELLO_AGENT_LIST_ID=REPLACE_ME   open the board with .json on the end to find list ids
    TRELLO_REVIEW_LIST_ID=REPLACE_ME
"""
import os

import requests

API = "https://api.trello.com/1"


def _auth():
    key, token = os.environ.get("TRELLO_KEY", ""), os.environ.get("TRELLO_TOKEN", "")
    if not key or not token:
        raise RuntimeError("TRELLO_KEY and TRELLO_TOKEN must both be set in .env")
    return {"key": key, "token": token}


def fetch_agent_tasks():
    list_id = os.environ["TRELLO_AGENT_LIST_ID"]
    r = requests.get(f"{API}/lists/{list_id}/cards", params=_auth(), timeout=30)
    r.raise_for_status()
    return [{
        "id": c["id"],
        "title": c.get("name", ""),
        "description": c.get("desc") or "",
        "definition_of_done": "",
    } for c in r.json()]


def post_result(task, text):
    r = requests.post(
        f"{API}/cards/{task['id']}/actions/comments",
        params={**_auth(), "text": text},
        timeout=30,
    )
    r.raise_for_status()


def move_to_review(task):
    r = requests.put(
        f"{API}/cards/{task['id']}",
        params={**_auth(), "idList": os.environ["TRELLO_REVIEW_LIST_ID"]},
        timeout=30,
    )
    r.raise_for_status()
