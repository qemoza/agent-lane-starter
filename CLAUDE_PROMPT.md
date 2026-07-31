# Paste this into Claude Code

Open your terminal in this folder, run `claude`, and paste everything below the line.

---

I want to put an AI agent inside the task board I already use.

The idea: I add one lane to my board called AGENT. When I drag a card into that lane, an agent picks it up, does the work, posts what it did back on the card, and moves the card to review. I check it. I stop doing the work myself and start scoping and reviewing.

This repo has the pieces. Read these files before you do anything, so you know what already exists and do not rebuild it:

- `README.md` — what this is and the four pieces it needs
- `agent_loop.py` — the loop that watches the lane and runs you
- `boards/` — adapters for ClickUp, Trello and GitHub
- `context/KNOWLEDGE_BASE.md` and `context/SOPS.md` — the templates I fill in
- `.env.example` — every setting the loop reads
- `VPS_SETUP.md` — how it runs on a server so it never sleeps

Now walk me through setup, one step at a time. Wait for my answer before moving on. Do not do all of it at once.

**Step 1. Which board.**
Ask me which tool my tasks live in. If it is ClickUp, Trello or GitHub, use that adapter. If it is something else (Notion, Linear, Asana, Monday, a spreadsheet), copy the closest adapter in `boards/` and write a new one for my tool. It needs the same three functions: `fetch_agent_tasks`, `post_result`, `move_to_review`. Look up the current API docs before you write it. Do not guess endpoints.

**Step 2. Keys and ids.**
Tell me exactly where to click to get my API key and my list or repo id. Then have me put them in `.env`. Never write a key into a tracked file, never paste one back to me in the chat, and never commit `.env`.

**Step 3. Make the lane.**
Tell me what to create in my board: a status or list called AGENT, and one called REVIEW. Then confirm the names in `.env` match what I actually made, because a mismatch here fails silently and looks like the agent is ignoring me.

**Step 4. Prove it works, small.**
Have me make one tiny throwaway task. Something with an obvious right answer that takes you under a minute. Move it to the AGENT lane. Run `python3 agent_loop.py --dry` first so I can see it found the card. Then run `python3 agent_loop.py --once` and we watch the comment come back. Do not move on until I confirm I saw the result on the card.

**Step 5. Give it my context.**
This is the step that decides whether the output is generic or mine, so do not rush it. Interview me and write the answers into `context/KNOWLEDGE_BASE.md`:

- what my business does and who buys from me
- how I talk (paste in something I wrote, and copy the register)
- what I sell and roughly how it is priced
- who is on my team and who does what
- the tools my work lives in

Then write two or three real SOPs into `context/SOPS.md` for jobs I actually repeat. Ask me to talk one through out loud and write down the steps I say. A specific SOP beats a clever prompt every time.

**Step 6. Give it tools.**
Ask what I need it to reach: my docs, my drive, my chat, my database, my calendar. Wire those up as MCP servers or scripts it can call. An agent with no connections can write me a paragraph and nothing else. Set up one connection, prove it with a real task, then add the next. Never add five at once.

**Step 7. Make it never sleep.**
When I am happy running it by hand, follow `VPS_SETUP.md` with me and put it on a small server. Show me how to read the logs and how to stop it.

**Rules for the whole thing.**

- One step at a time. Wait for me.
- Show me the exact command and what I should expect to see. If I see something different, we stop and fix it before moving on.
- Keep the agent's output as a draft. It reports back and a human approves. It does not email anyone, message anyone, or publish anything by itself.
- If something does not work, say so plainly and tell me what you tried. Do not tell me it worked and hope.
- Explain things in plain words. Assume I can follow instructions but do not write code for a living.
