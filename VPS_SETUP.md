# Run it on a server so it never sleeps

Your laptop closes. The agent stops. That is the only reason this step exists.

Any small cloud machine works. Hostinger, Hetzner, DigitalOcean, Vultr. The
cheapest tier is enough, because the model does the thinking somewhere else. Expect
a few dollars a month.

## What you need

- Ubuntu 22.04 or newer
- 1 shared CPU and 1 GB of memory is fine
- Node 18 or newer, and Python 3.10 or newer

## Set it up

```bash
ssh root@YOUR_SERVER_IP

apt update && apt install -y python3-pip git
curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt install -y nodejs
npm install -g @anthropic-ai/claude-code

git clone https://github.com/qemoza/agent-lane-starter
cd agent-lane-starter
pip3 install -r requirements.txt
cp .env.example .env
nano .env          # paste your keys and ids, then Ctrl+O, Enter, Ctrl+X
```

Log Claude Code in once, as yourself:

```bash
claude
```

It prints a link. Open it on your own computer, approve, come back. That login
stays on the server.

## Prove it before you automate it

```bash
python3 agent_loop.py --dry     # does it see the card you put in the lane
python3 agent_loop.py --once    # does the comment come back
```

Do not skip this. A service that starts cleanly and does nothing looks identical to
a service that is working.

## Keep it running

```bash
cat >/etc/systemd/system/agent-lane.service <<'EOF'
[Unit]
Description=Agent Lane
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/agent-lane-starter
ExecStart=/usr/bin/python3 /root/agent-lane-starter/agent_loop.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now agent-lane
```

## Watch it

```bash
systemctl status agent-lane        # is it alive
journalctl -u agent-lane -f        # what is it doing right now
systemctl restart agent-lane       # after you change .env
systemctl stop agent-lane          # stop it
```

`Restart=always` brings it back after a crash or a reboot. It cannot help if the
process is alive but stuck, so read the logs now and then and check the timestamps
are recent.

## Before you leave it alone

- **Point `AGENT_WORKDIR` at a repo you can throw away first.** Watch what it does
  for a week before you aim it at anything that matters.
- **Give the server its own keys**, not the ones on your laptop, so you can turn
  off just this machine.
- **`.env` holds live keys.** It is in `.gitignore`. Keep it that way.
- **Costs run while you sleep.** That is the point, and it is also the risk. Set a
  spend limit in your Anthropic account before the first overnight run.
