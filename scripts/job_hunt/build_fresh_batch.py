#!/usr/bin/env python3
"""Filter the agent's fresh targets: drop already-contacted, verify deliverability,
keep only bounce-safe (valid/catch_all), write a sendable batch JSON."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from verify_emails import verify  # noqa

SRC = "data/job-hunt/targets-fresh-2026-06-20.json"
OUT = "data/job-hunt/batch-2026-06-20-c.json"

# companies / emails already emailed today — never repeat
CONTACTED = {"raven", "businessonbot", "floworks", "superkalam", "bolna",
             "yellow", "scalenut", "signzy", "leena", "gnani", "limechat",
             "coulomb", "peoplebox", "krutrim"}

with open(SRC) as f:
    items = json.load(f)

batch, skipped = [], []
seen_domains = set()
for it in items:
    comp = (it.get("company") or "").lower()
    email = (it.get("email") or "").strip()
    if not email or "@" not in email:
        skipped.append((comp, email, "no-email")); continue
    if any(c in comp for c in CONTACTED):
        skipped.append((comp, email, "already-contacted")); continue
    dom = email.split("@")[1].lower()
    if dom in seen_domains:
        skipped.append((comp, email, "dup-domain")); continue
    v = verify(email)
    print(f"  {v['verdict']:>10}  {email:<32} {comp} ({v['reason']})")
    if v["verdict"] in ("valid", "catch_all"):
        if not it.get("subject") or not it.get("body"):
            skipped.append((comp, email, "no-email-body")); continue
        batch.append({"to": email, "subject": it["subject"], "body": it["body"]})
        seen_domains.add(dom)
    else:
        skipped.append((comp, email, v["verdict"]))

with open(OUT, "w") as f:
    json.dump(batch, f, indent=2)

print(f"\nBOUNCE-SAFE TO SEND: {len(batch)}  ->  {OUT}")
print(f"skipped: {len(skipped)}")
for c, e, why in skipped:
    print(f"   - {c:<18} {e:<32} {why}")
