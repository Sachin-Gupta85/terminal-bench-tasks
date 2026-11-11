# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends gawk jq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

Add task environment with seeded logsRUN python - <<'EOF'
import os, random
from datetime import datetime, timedelta

random.seed(42)
os.makedirs("/app/logs", exist_ok=True)
services = ["auth", "billing", "gateway", "search", "notifier", "worker"]
levels = ["INFO"] * 6 + ["DEBUG"] * 3 + ["WARN"] * 2 + ["ERROR"] * 2
# decoys an agent should not count as ERROR
decoys = ["error", "ERRORS", "Error"]
start = datetime(2026, 1, 1)

for day in range(3):
    with open(f"/app/logs/app-{day + 1}.log", "w") as f:
        for i in range(400):
            ts = (start + timedelta(days=day, seconds=i * 37)).isoformat()
            level = random.choice(levels)
            if random.random() < 0.03:
                level = random.choice(decoys)
            svc = random.choice(services)
            msg = random.choice([
                "request completed", "cache miss", "timeout talking to db",
                "retrying job", "ERROR in upstream response", "user login",
            ])
            f.write(f"{ts} {level} {svc} {msg}\n")
EOF
