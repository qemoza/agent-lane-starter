# Agent Lane — put AI agents inside the task list you already have

**Written walkthrough:** [I Put AI Agents Inside My Task List](https://www.qemoza.ai/blog/i-put-ai-agents-inside-my-task-list) on the Qemoza blog.

You have a board. Backlog, this week, doing, done. Add one more lane and call it **AGENT**.

Drop a card in that lane and something else does the work. It reads the task, does the job, and hands it back for you to check.

You stop building. You scope and you review.

From this video: [I Tagged a Task and an AI Agent Built It](https://www.youtube.com/@Hamzaouladd)

## Do not build a new system

You already have a board. ClickUp, Notion, Trello, GitHub, Linear, a spreadsheet. Use that one. Humans and agents work the same board, and you never learn a second tool.

## The four pieces

1. **A board with a trigger.** Moving a card into the AGENT lane is the signal. That is the whole trigger.
2. **The agent.** Claude Code, running headless on a machine.
3. **A place for it to live.** A small server so it keeps working when your laptop is shut.
4. **The glue.** About 200 lines that watch the lane, run the agent, and post the answer back. That is `agent_loop.py` in this repo.

## What you get here

| File | What it is |
| --- | --- |
| `CLAUDE_PROMPT.md` | Paste this into Claude Code. It sets the whole thing up with you, step by step. |
| `agent_loop.py` | The glue. Watches the lane, runs the agent, writes the result back. |
| `boards/` | Adapters for ClickUp, Trello, and GitHub. Copy one to add your own. |
| `context/` | Two templates: what your business knows, and how your business does things. |
| `VPS_SETUP.md` | Get it running on a small server so it never sleeps. |

## Fastest way to start

1. Install [Claude Code](https://claude.com/claude-code).
2. Clone this repo and open it in your terminal.
3. Run `claude` and paste the contents of `CLAUDE_PROMPT.md`.
4. Answer its questions. It wires your board, your keys, and your first task.

Claude reads the code in here and does the setup with you. You do not have to understand `agent_loop.py` to run it.

## Or by hand

```bash
git clone https://github.com/qemoza/agent-lane-starter
cd agent-lane-starter
pip install -r requirements.txt
cp .env.example .env          # fill in your board key and ids
python3 agent_loop.py --once  # one pass, so you can watch it work
```

Add a card, move it to your AGENT lane, run it again. Watch what comes back.

## Make it actually good

A bare agent can talk. It cannot do much. Three things turn it into a worker.

**Give it tools.** Connect the things you already use. Your docs, your drive, your chat, your database. With no connections it can only write you a paragraph. With connections it can go get the file, read the thread, and change the record.

**Give it context.** Two kinds, and they are different.

- *Knowledge base:* how you work. Your voice, your offer, the way you like things done. Put it in `context/KNOWLEDGE_BASE.md`.
- *Database:* what actually happened. Every call, every message, the real history. Point it at that in your `.env`.

**Give it SOPs.** "Prep me for a call" gets you something generic. "Prep me for a call, and here is exactly how I prep" gets you your version. Write those steps down once in `context/SOPS.md` and it does it your way every time.

## Being honest with you

This is not a weekend build. Getting it to know a real business takes weeks, not hours, because you have to hand it all the context that currently lives in your head.

Creative work is the easy half. Drafting, research, summarising, sorting. That works quickly.

Code is the hard half. It needs structure, a repo it understands, and a way to check its own work. Expect that part to take real effort.

Cost is pay as you go. You pay for model usage per run, plus a few dollars a month for the server. It is not free.

## One rule

The agent hands work back. It does not ship and it does not message anyone. You approve, then it goes out.

Keep it that way until you trust it, which takes longer than you think.

## Licence

MIT. Do what you like with it.
