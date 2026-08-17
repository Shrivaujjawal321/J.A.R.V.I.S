# Implementation Runbook: Postmark Authenticated Sending

**Companion to SOP OPS-EMAIL-001 — concrete, step-by-step Postmark setup**

| Field | Value |
|---|---|
| Document ID | OPS-EMAIL-001-A |
| Version | 1.0 |
| Parent SOP | OPS-EMAIL-001 (Authenticated Email Sending Infrastructure) |
| ESP | Postmark |
| Sending subdomain | `mail.company.com` *(replace with real subdomain)* |
| Status | Active |

> **Placeholder convention:** every `company.com` / `mail.company.com` / `<...>` below is a placeholder. Replace with the real domain. Values marked *(Postmark-generated)* only appear inside the Postmark console after you add the domain — you cannot pre-write them.

---

## 0. Important scope note — what Postmark is (and isn't) for

- **Use Postmark for TRANSACTIONAL mail** — password resets, receipts, verification codes, system notifications, alerts. Postmark's inbox rate here is excellent.
- **Do NOT run cold outreach / purchased lists / unsolicited marketing through Postmark.** Postmark's Terms of Service prohibit it and will suspend the account. If the company needs a cold-outreach stream, provision that separately (Amazon SES + explicit opt-in, or a dedicated outreach platform) under its own subdomain.
- For opt-in newsletters / product updates, use Postmark's **Broadcast** message stream (separate reputation, requires unsubscribe).

---

## 1. Prerequisites

- [ ] Postmark account created, on a plan matching expected volume.
- [ ] DNS admin access to the domain (registrar / DNS provider console).
- [ ] Decision recorded: sending subdomain = `mail.company.com`. For stream isolation, optionally `txn.company.com` (transactional) separate from `news.company.com` (broadcast).
- [ ] A reachable mailbox for DMARC reports, e.g. `dmarc-reports@company.com`.

---

## 2. Create the Server and Message Streams

1. Postmark console → **Servers** → **Create Server**. Name it e.g. `Production`.
2. Inside the server, open **Message Streams**. Postmark gives you by default:
   - **Transactional** (type: Transactional) — for all system/transactional mail.
   - **Broadcast** (type: Broadcast) — only if you send opt-in bulk/newsletters.
3. Keep transactional and broadcast on **separate streams** — they carry separate reputation. Never send bulk on the transactional stream.

---

## 3. Add and verify the sending domain

1. Console → **Sender Signatures** → **Domains** tab → **Add Domain**.
2. Enter `mail.company.com`.
3. Postmark now shows two records to publish — **DKIM** and **Return-Path**. Both are required for full alignment.

### 3.1 DKIM record

Postmark shows a TXT record (values are *Postmark-generated*):

```
Type : TXT
Host : <selector>._domainkey.mail.company.com     (Postmark shows the exact selector)
Value: k=rsa; p=<long-public-key>                 (Postmark-generated)
TTL  : 3600
```

Publish it exactly as shown. Postmark uses a 2048-bit key by default.

### 3.2 Return-Path (custom) record — this is what makes SPF align

Postmark sends with its own bounce infrastructure; a **custom Return-Path CNAME** points a subdomain of yours at Postmark so SPF authenticates and **aligns to your domain** under DMARC.

```
Type : CNAME
Host : pm-bounces.mail.company.com                (Postmark shows the exact host)
Value: pm.mtasv.net                               (Postmark-generated target)
TTL  : 3600
```

> Because the custom Return-Path lives on your domain and resolves to Postmark, you do **not** need to add Postmark to your own `v=spf1` record. SPF is evaluated on the `pm-bounces` subdomain (Postmark's SPF) and aligns to `company.com` via DMARC relaxed alignment.

### 3.3 Confirm in console

Back in Postmark → **Domains** → your domain → click **Verify**. Wait until **DKIM = Verified** and **Return-Path = Verified** (green). DNS propagation can take minutes to a few hours.

---

## 4. Publish the DMARC policy

DMARC is on **your** domain, not set by Postmark. Add it and roll out in stages (see parent SOP §7.4).

```
Type : TXT
Host : _dmarc.company.com
Value: v=DMARC1; p=none; rua=mailto:dmarc-reports@company.com; adkim=r; aspf=r; pct=100
TTL  : 3600
```

- Start `p=none` for 1–2 weeks, watch reports.
- Move to `p=quarantine; pct=25` → ramp `pct` to 100.
- Finish at `p=reject`.
- Use **relaxed alignment** (`adkim=r; aspf=r`) with Postmark — the custom Return-Path aligns at the organizational-domain level, so relaxed is correct. Strict (`s`) can fail with the `pm-bounces` subdomain.

Postmark also offers **free weekly DMARC monitoring** — enable it at [dmarc.postmarkapp.com](https://dmarc.postmarkapp.com) using this same `rua` mailbox.

---

## 5. Rotating / per-purpose "From" addresses

Once the **domain** signature is verified, Postmark lets you send from **any** local-part on that domain — you do not verify each address individually.

- `verify-8f2a@mail.company.com`, `receipt-9d1c@mail.company.com`, `noreply@mail.company.com` — all inherit DKIM + Return-Path alignment automatically.
- Application generates the local-part at runtime; DKIM signs with the one domain key → **every send passes**.
- **Rule:** the `From:` domain must be exactly `mail.company.com` (the verified domain). A `From:` on any other domain will not align.

---

## 6. Wire the application to send

**Option A — HTTP API (recommended)**

```bash
curl "https://api.postmarkapp.com/email" \
  -X POST \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-Postmark-Server-Token: <SERVER_API_TOKEN>" \
  -d '{
    "From": "receipt-8f2a@mail.company.com",
    "To": "customer@example.com",
    "Subject": "Your receipt",
    "HtmlBody": "<p>Thanks for your order.</p>",
    "MessageStream": "transactional"
  }'
```

**Option B — SMTP**

```
Host    : smtp.postmarkapp.com
Port    : 587 (STARTTLS)
Username: <SERVER_API_TOKEN>
Password: <SERVER_API_TOKEN>     (same token)
```

- Store `<SERVER_API_TOKEN>` in the secrets manager / env — never in code or git.
- Always set `MessageStream` explicitly (`transactional` or `broadcast`).

---

## 7. Verification gate — must pass before go-live

Run parent SOP §9. Postmark-specific confirmations:

- [ ] Postmark console: DKIM **Verified** + Return-Path **Verified** (both green).
- [ ] `dig +short TXT <selector>._domainkey.mail.company.com` returns the key.
- [ ] `dig +short CNAME pm-bounces.mail.company.com` returns `pm.mtasv.net`.
- [ ] `dig +short TXT _dmarc.company.com` returns the DMARC record.
- [ ] Send one real message → **https://www.mail-tester.com** → score **≥ 9/10**, `spf=pass`, `dkim=pass`, `dmarc=pass`.
- [ ] Gmail "Show original": SPF PASS, DKIM PASS, DMARC PASS, and `mailed-by`/`signed-by` show `mail.company.com`.
- [ ] Enroll `mail.company.com` in **Google Postmaster Tools**.

---

## 8. Broadcast (opt-in bulk) — extra requirements

Only if using the Broadcast stream:

- [ ] Recipients are **opt-in** (no purchased/scraped lists — Postmark enforces this).
- [ ] `List-Unsubscribe` + `List-Unsubscribe-Post` headers present; Postmark adds a managed unsubscribe link — keep it.
- [ ] Physical postal address + clear sender identity in footer.
- [ ] Suppression list honored automatically by Postmark — do not override.

---

## 9. Monitoring (Postmark specifics)

| Cadence | Action |
|---|---|
| Daily | Postmark **Activity** feed — bounces, spam complaints. Keep bounce < 2%, complaints < 0.1%. |
| Weekly | Postmark DMARC weekly digest — confirm 100% pass; investigate unknown sources. |
| Monthly | Google Postmaster reputation trend = High/Good. |
| Quarterly | Rotate DKIM (Postmark → Domain → regenerate DKIM → publish new TXT → verify → old auto-retires). |
| On change | Re-run §7 gate after any DNS or Postmark change. |

---

## 10. Troubleshooting (Postmark)

| Symptom | Cause | Fix |
|---|---|---|
| Domain won't verify | DNS not propagated / typo in host | Re-check exact host string from console; wait; `dig` to confirm. |
| `dmarc=fail`, SPF/DKIM pass | Strict alignment set | Switch DMARC to `adkim=r; aspf=r` (relaxed) — required with Postmark Return-Path. |
| Return-Path shows Postmark domain, not yours | Custom Return-Path CNAME missing | Publish the `pm-bounces` CNAME → re-verify. |
| Sends blocked / account paused | Cold/bulk mail on transactional stream, or ToS violation | Move to Broadcast with opt-in only; contact Postmark support; use SES for cold outreach. |
| Mail in spam despite pass | Content / new domain / no warmup | Warm up (parent SOP §10); review content; check blocklists. |

---

## 11. Sign-off

| Role | Name | Date |
|---|---|---|
| Infra Owner | | |
| Security | | |

**Recorded:** ESP = Postmark · Sending domain = `mail.company.com` · DMARC target policy = `p=reject`

---
*End of Runbook OPS-EMAIL-001-A v1.0 — companion to OPS-EMAIL-001*
