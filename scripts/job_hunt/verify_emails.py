#!/usr/bin/env python3
"""
Free email verifier for the job-outreach engine — no paid API.

For each address: MX lookup + SMTP RCPT probe + catch-all detection.
Verdicts:
  valid      -> server accepts the mailbox      -> SAFE to cold-email
  invalid    -> server rejects (550/551/553)    -> DO NOT send (would bounce)
  catch_all  -> domain accepts everything        -> RISKY -> route to LinkedIn
  unknown    -> SMTP blocked/greylisted/timeout  -> RISKY -> route to LinkedIn

Usage:
  python scripts/job_hunt/verify_emails.py addr1@x.com addr2@y.com ...
  python scripts/job_hunt/verify_emails.py --file emails.txt
Prints a verdict line per address and a JSON summary at the end.
"""
import sys
import json
import smtplib
import socket
import random
import string
import argparse

try:
    import dns.resolver
except ImportError:
    print("ERROR: dnspython not installed (.venv/bin/pip install dnspython)", file=sys.stderr)
    sys.exit(2)

MAIL_FROM = "outreach-check@example.com"  # probe identity only; never sends a message
TIMEOUT = 10


def mx_hosts(domain):
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=TIMEOUT)
        return [str(r.exchange).rstrip(".") for r in sorted(answers, key=lambda r: r.preference)]
    except Exception:
        return []


def _rcpt(server, addr):
    """Return SMTP code for RCPT TO:<addr>. -1 on error."""
    try:
        code, _ = server.rcpt(addr)
        return code
    except Exception:
        return -1


def verify(email):
    if "@" not in email:
        return {"email": email, "verdict": "invalid", "reason": "malformed"}
    domain = email.rsplit("@", 1)[1].lower()
    hosts = mx_hosts(domain)
    if not hosts:
        return {"email": email, "verdict": "invalid", "reason": "no MX record"}

    for host in hosts[:2]:  # try top 2 MX
        try:
            server = smtplib.SMTP(timeout=TIMEOUT)
            server.connect(host)
            server.helo("example.com")
            server.mail(MAIL_FROM)
            # catch-all probe: a random mailbox that should not exist
            rnd = "".join(random.choices(string.ascii_lowercase, k=16)) + "@" + domain
            rnd_code = _rcpt(server, rnd)
            real_code = _rcpt(server, email)
            server.quit()
            if rnd_code in (250, 251):
                return {"email": email, "verdict": "catch_all",
                        "reason": f"domain accepts all (rnd={rnd_code})"}
            if real_code in (250, 251):
                return {"email": email, "verdict": "valid", "reason": f"RCPT {real_code}"}
            if real_code in (550, 551, 552, 553, 554):
                return {"email": email, "verdict": "invalid", "reason": f"RCPT {real_code}"}
            return {"email": email, "verdict": "unknown", "reason": f"RCPT {real_code}"}
        except (socket.timeout, smtplib.SMTPException, OSError) as e:
            last = str(e)
            continue
    return {"email": email, "verdict": "unknown", "reason": f"SMTP blocked: {last}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("emails", nargs="*")
    ap.add_argument("--file", help="file with one email per line")
    args = ap.parse_args()
    emails = list(args.emails)
    if args.file:
        with open(args.file) as f:
            emails += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    if not emails:
        ap.error("no emails given")

    results = []
    for e in emails:
        r = verify(e)
        results.append(r)
        print(f"{r['verdict']:>10}  {r['email']:<40} ({r['reason']})")

    summary = {}
    for r in results:
        summary[r["verdict"]] = summary.get(r["verdict"], 0) + 1
    safe = [r["email"] for r in results if r["verdict"] == "valid"]
    print("\n--- summary ---")
    print(json.dumps(summary, indent=2))
    print(f"SAFE TO SEND ({len(safe)}): {', '.join(safe) if safe else 'none'}")


if __name__ == "__main__":
    main()
