#!/usr/bin/env python3
"""The glue between your board and the agent.

Watch one lane. When a card lands in it, run Claude Code on that task, then write
the result back to the card and move it to your review lane.

    python3 agent_loop.py --once     one pass, then stop (start here)
    python3 agent_loop.py            keep polling every POLL_SECONDS
    python3 agent_loop.py --dry      show what it would pick up, run nothing

Everything board-specific lives in boards/. This file never knows which board you use.
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent


def load_env():
    """Read .env into os.environ without a dependency. Existing vars win."""
    f = ROOT / ".env"
    if not f.exists():
        sys.exit("No .env found. Copy .env.example to .env and fill it in.")
    for line in f.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def get_board():
    """Pick the adapter named in BOARD. Each adapter exposes the same three calls."""
    name = os.environ.get("BOARD", "").strip().lower()
    if not name:
        sys.exit("Set BOARD in .env to one of: clickup, trello, github")
    try:
        mod = __import__(f"boards.{name}", fromlist=["*"])
    except ImportError:
        sys.exit(f"No adapter for '{name}'. Look in boards/ or copy one to make your own.")
    for fn in ("fetch_agent_tasks", "post_result", "move_to_review"):
        if not hasattr(mod, fn):
            sys.exit(f"boards/{name}.py is missing {fn}()")
    return mod


def build_prompt(task):
    """Task + how you work + how you do this job = what the agent actually sees.

    The context files are the whole difference between a generic answer and yours.
    An empty context/ still runs; it just gives you generic work.
    """
    parts = []
    for path, header in (
        (ROOT / "context" / "KNOWLEDGE_BASE.md", "HOW THIS BUSINESS WORKS"),
        (ROOT / "context" / "SOPS.md", "HOW WE DO THINGS, STEP BY STEP"),
    ):
        if path.exists():
            body = path.read_text().strip()
            if body:
                parts.append(f"# {header}\n\n{body}")

    parts.append(
        "# YOUR TASK\n\n"
        f"Title: {task['title']}\n\n"
        f"Details:\n{task.get('description') or '(none given)'}\n\n"
        f"Done means:\n{task.get('definition_of_done') or '(not stated — say what you assumed)'}"
    )
    parts.append(
        "# HOW TO ANSWER\n\n"
        "Do the work. Then report back in this shape:\n"
        "1. What you did.\n"
        "2. What you produced, or where you put it.\n"
        "3. Anything you assumed, and anything you could not finish.\n\n"
        "Do not send anything to anyone. Do not publish. A human reviews this next."
    )
    return "\n\n---\n\n".join(parts)


def run_agent(prompt, workdir, timeout):
    """Run Claude Code headless. Returns (ok, text).

    --permission-mode acceptEdits lets it write files in workdir without stopping to
    ask. It still cannot reach anything you have not given it a tool for.
    """
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--permission-mode", "acceptEdits",
    ]
    try:
        r = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return False, "Claude Code is not installed, or `claude` is not on PATH."
    except subprocess.TimeoutExpired:
        return False, f"The agent ran past {timeout}s and was stopped."

    if r.returncode != 0:
        return False, f"The agent exited {r.returncode}.\n\n{(r.stderr or '').strip()[:2000]}"

    # --output-format json gives one object with the final text in `result`.
    try:
        return True, json.loads(r.stdout)["result"]
    except (json.JSONDecodeError, KeyError):
        # Never lose the work just because the envelope changed shape.
        return True, r.stdout.strip()


def handle(task, board, workdir, timeout, dry):
    print(f"  → {task['id']}  {task['title'][:70]}")
    if dry:
        return
    ok, text = run_agent(build_prompt(task), workdir, timeout)
    status = "Agent finished" if ok else "Agent could not finish"
    board.post_result(task, f"**{status}**\n\n{text}")
    if ok:
        board.move_to_review(task)
        print("    posted, moved to review")
    else:
        # Leave it in the lane. A failed task that silently moves on is a task you
        # never hear about again.
        print(f"    FAILED, left in the lane: {text.splitlines()[0][:90]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="one pass, then exit")
    ap.add_argument("--dry", action="store_true", help="list what it would pick up, run nothing")
    a = ap.parse_args()

    load_env()
    board = get_board()
    workdir = os.environ.get("AGENT_WORKDIR") or str(ROOT / "workspace")
    pathlib.Path(workdir).mkdir(parents=True, exist_ok=True)
    timeout = int(os.environ.get("AGENT_TIMEOUT_SECONDS", "1800"))
    poll = int(os.environ.get("POLL_SECONDS", "60"))

    print(f"board={os.environ.get('BOARD')}  workdir={workdir}  timeout={timeout}s")

    while True:
        try:
            tasks = board.fetch_agent_tasks()
        except Exception as e:
            # A board hiccup must not kill the loop. It runs unattended for weeks.
            print(f"could not read the board: {e}")
            tasks = []

        if tasks:
            print(f"{len(tasks)} task(s) in the agent lane")
            for t in tasks:
                try:
                    handle(t, board, workdir, timeout, a.dry)
                except Exception as e:
                    print(f"    error on {t['id']}: {e}")
        else:
            print("agent lane is empty")

        if a.once or a.dry:
            return
        time.sleep(poll)


if __name__ == "__main__":
    main()
