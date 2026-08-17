# SOP: Authenticated Email Sending Infrastructure

**Standard Operating Procedure — DNS-Validated Outbound Email**

| Field | Value |
|---|---|
| Document ID | OPS-EMAIL-001 |
| Version | 1.1 |
| Status | Active |
| Owner | Platform / Infrastructure Team |
| Review cycle | Quarterly |
| Applies to | All outbound email sent from company-owned domains |

---

## 1. Purpose

Establish a repeatable procedure so that **every email** sent from a company-owned domain — including dynamically generated ("temp"/rotating) addresses on that domain — reliably **passes SPF, DKIM, and DMARC authentication** at the receiving mail server, achieving inbox placement instead of spam/reject.

**This SOP covers only domains the company owns and controls.** It does not and cannot make addresses on third-party disposable-mail providers pass authentication — that is technically impossible and out of scope.

## 2. Scope

**In scope**
- Transactional email (receipts, password resets, notifications)
- Outreach / marketing email from company domains
- Rotating or per-purpose addresses generated on company subdomains (e.g. `req-8f2a@mail.company.com`)

**Out of scope**
- Sending from domains not owned by the company
- Bypassing any third party's anti-abuse / disposable-domain blocking
- Impersonating any other organization or individual

## 3. Definitions

| Term | Meaning |
|---|---|
| **SPF** | Sender Policy Framework — DNS TXT record listing IPs/services authorized to send for a domain. |
| **DKIM** | DomainKeys Identified Mail — cryptographic signature added to each message; public key published in DNS. |
| **DMARC** | Policy that tells receivers what to do when SPF/DKIM fail, and where to send reports. Requires **alignment**. |
| **Alignment** | The domain in `From:` must match the SPF/DKIM-authenticated domain. This is what actually makes DMARC "pass". |
| **Sending domain / subdomain** | Dedicated subdomain used for programmatic sends (e.g. `mail.company.com`), isolated from the corporate mailbox domain. |
| **ESP** | Email Service Provider (Amazon SES, Postmark, SendGrid, etc.) — or a self-hosted MTA (Postfix). |
| **rDNS / PTR** | Reverse DNS record mapping the sending IP back to a hostname. Required for self-hosted; managed by ESP otherwise. |

## 4. Roles & Responsibilities (RACI)

| Task | Infra | DevOps | Security | App Team |
|---|---|---|---|---|
| Own DNS zone & records | **R/A** | C | C | I |
| Provision ESP / MTA | R | **R/A** | C | I |
| Rotate DKIM keys | **R/A** | C | C | I |
| Configure app to send via authenticated relay | C | C | I | **R/A** |
| Monitor DMARC reports | C | **R/A** | C | I |
| Incident response (deliverability) | R | **R/A** | C | I |

R = Responsible, A = Accountable, C = Consulted, I = Informed.

---

## 5. Architecture Decisions (make these BEFORE setup)

Two decisions determine the whole build. This section states each option's pros and cons and the company's default choice. Record the final choice in the Approval table (Section 15).

### Decision 1 — Managed ESP vs Self-Hosted MTA

**Option A — Managed ESP** (Amazon SES, Postmark, SendGrid, Mailgun)

| Pros | Cons |
|---|---|
| IP reputation, rDNS/PTR, and warmup are handled for you | Per-email / monthly cost (grows with volume) |
| Built-in DKIM signing — one-click key generation | Less low-level control over headers/routing |
| Fast setup (hours, not days); scales elastically | Vendor lock-in; migration effort later |
| Compliance & DMARC-reporting add-ons available | New accounts start sandboxed (SES) — needs approval to exit |
| Removes ~80% of the deliverability failure surface | On cheap shared-IP tiers, a bad neighbor can dent reputation |

**Option B — Self-Hosted MTA** (Postfix + OpenDKIM on a static IP)

| Pros | Cons |
|---|---|
| Full control over routing, headers, and infrastructure | **You** own IP reputation, warmup, and blocklist recovery |
| No per-email cost at scale | Must set rDNS/PTR, secure the box, patch, and monitor 24/7 |
| Data stays fully in-house (privacy/compliance edge) | New IPs are cold and often pre-flagged — deliverability is hard |
| No vendor sending limits | Significant ongoing ops burden and on-call load |
| | Needs a static IP that is not on any blocklist |

> **Company default: Option A — Managed ESP.**
> Use **Amazon SES** for high-volume / cost-sensitive sending, or **Postmark** for transactional mail where deliverability and analytics matter most and volume is moderate.
> Choose Option B (self-host) **only** with a documented, security-approved reason (e.g. strict data-residency mandate) and dedicated ops ownership.

**SES vs Postmark quick guide**

| | Amazon SES | Postmark |
|---|---|---|
| Best for | Bulk + transactional, lowest cost | Transactional, best-in-class inbox rate |
| Price model | ~$0.10 / 1,000 emails | Higher per-email, flat tiers |
| Deliverability tooling | Good (needs config) | Excellent out of the box |
| Setup speed | Sandbox → request production | Fast, minimal gating |

### Decision 2 — Root Domain vs Dedicated Subdomain

**Option A — Dedicated Subdomain** (`mail.company.com`)

| Pros | Cons |
|---|---|
| **Reputation isolation** — a spam incident never touches the domain used for human mailboxes | Slightly more DNS setup up front |
| Per-subdomain DMARC policy — enforce `p=reject` on sending without risking corporate mail | Subdomain reputation starts cold — needs warmup |
| Clean separation of streams (`mktg.` vs `txn.` subdomains) with independent reputations | Some receivers still factor in the organizational domain |
| Safe place to experiment without collateral damage | |

**Option B — Root Domain** (`company.com`)

| Pros | Cons |
|---|---|
| Simplest — one domain, one set of records | A deliverability/spam incident damages **both** sending and the human-mailbox domain |
| May inherit existing established domain trust | Cannot segment transactional vs marketing reputation |
| | Forced to keep DMARC lenient because corporate mail shares the policy — weaker protection |
| | Highest blast radius if the domain gets blocklisted |

> **Company default: Option A — Dedicated Subdomain.**
> Use `mail.company.com` as the base. For meaningful volume, split streams:
> `txn.company.com` (transactional) and `mktg.company.com` (marketing/outreach), each with its own DKIM key and DMARC policy, so a marketing complaint spike can never affect password-reset delivery.

---

## 6. Prerequisites

Before starting, confirm you have:

- [ ] A company-owned domain with **DNS admin access** (registrar or DNS provider console).
- [ ] Decisions 1 and 2 from Section 5 recorded and approved.
- [ ] An **ESP account** (default) **or** a hardened self-hosted MTA on a static IP with rDNS control.
- [ ] Access to a terminal with `dig` (or `nslookup`) for verification.

---

## 7. Procedure — One-Time Setup

### Step 7.1 — Choose and register the sending subdomain

Per Decision 2, use a dedicated subdomain so a deliverability incident never contaminates the primary domain used for human mailboxes (Google Workspace / M365).

```
Corporate mailboxes : company.com          (leave untouched)
Programmatic sending: mail.company.com      (this SOP configures)
```

### Step 7.2 — Publish the SPF record

Add **one** TXT record on the sending subdomain. Include only the services that actually send.

```
Type : TXT
Host : mail.company.com
Value: v=spf1 include:amazonses.com -all
TTL  : 3600
```

Rules:
- Exactly **one** SPF record per domain (multiple = permanent fail).
- Keep DNS lookups ≤ 10 (each `include:` counts).
- End with `-all` (hard fail) once verified; use `~all` (soft fail) only during initial testing.

### Step 7.3 — Configure DKIM signing

1. In the ESP console, add `mail.company.com` as a sending domain and request **DKIM keys** (use 2048-bit).
2. The ESP returns CNAME (SES) or TXT (Postmark) records. Publish them exactly:

```
# Amazon SES example (3 CNAMEs)
Type : CNAME
Host : <selector1>._domainkey.mail.company.com
Value: <selector1>.dkim.amazonses.com
TTL  : 3600
(repeat for selector2, selector3)
```

3. Wait for the ESP to report **"Verified"** before sending.

Self-hosted (Postfix + OpenDKIM): generate a keypair, publish the public key as a TXT record at `<selector>._domainkey.mail.company.com`, keep the private key `chmod 600`, restart OpenDKIM.

### Step 7.4 — Publish the DMARC policy

Start in **monitor mode** to gather data without risking legit mail, then tighten.

```
Type : TXT
Host : _dmarc.mail.company.com
Value: v=DMARC1; p=none; rua=mailto:dmarc-reports@company.com; adkim=s; aspf=s; pct=100
TTL  : 3600
```

Progression (do NOT skip stages):
1. `p=none` — observe reports for **1–2 weeks**.
2. `p=quarantine; pct=25` → raise `pct` gradually to 100 once reports show 100% pass.
3. `p=reject` — final enforced state.

`adkim=s; aspf=s` = strict alignment (highest trust). Relax to relaxed (`r`) only if a legitimate subdomain send fails alignment.

### Step 7.5 — (Self-hosted only) Reverse DNS + MX + TLS

- Set the **PTR record** for the sending IP to `mail.company.com` (request via your host/ISP).
- Ensure the IP is **not on any blocklist** (check Spamhaus, Barracuda).
- Enable **opportunistic TLS** on the MTA.
- Managed ESP users skip this — the ESP owns it.

### Step 7.6 — (Optional) MTA-STS + TLS-RPT + BIMI

For maximum trust once the above is stable:
- **MTA-STS**: enforce TLS on inbound to your domain.
- **BIMI**: display the company logo in supporting inboxes (requires `p=quarantine`+ and a VMC in most cases).

---

## 8. Procedure — Generating Rotating / "Temp" Addresses (Correctly)

Because the addresses live on **your own** authenticated domain, they inherit full SPF/DKIM/DMARC pass. Two supported patterns:

**Pattern A — Catch-all subdomain**
- Configure the ESP/MTA to accept any local-part on `mail.company.com`.
- Application generates addresses on demand: `job-4f8a2@mail.company.com`, `verify-9d1c@mail.company.com`.
- All sign with the same DKIM key → all pass authentication.

**Pattern B — Plus/subaddressing**
- Single real mailbox `outreach@company.com` + tags: `outreach+campaign-x@company.com`.
- No new DNS work; routing by tag.

**Rule:** The `From:` domain of every generated address MUST be the authenticated sending domain (or an aligned subdomain). Never set `From:` to a domain you have not configured — alignment will fail.

---

## 9. Verification — "Passes Everytime" Gate

**No sending configuration is considered complete until it passes all four checks.** Re-run after any DNS change.

### 9.1 DNS record presence (CLI)

```bash
dig +short TXT mail.company.com                       # SPF present, single record
dig +short CNAME selector1._domainkey.mail.company.com # DKIM resolves
dig +short TXT _dmarc.mail.company.com                 # DMARC present
```

### 9.2 End-to-end authentication test

1. Send a real message through the production path to **check-auth@verifier.port25.com** or use **https://www.mail-tester.com** (send to the address it gives, then read the score).
2. **Pass criteria:** `spf=pass`, `dkim=pass`, `dmarc=pass`, alignment `pass`, mail-tester score **≥ 9/10**.

### 9.3 Inbox placement spot-check

Send to seed accounts on Gmail, Outlook/Office365, Yahoo. Open **Show original** (Gmail) → confirm `SPF: PASS`, `DKIM: PASS`, `DMARC: PASS`.

### 9.4 Reputation dashboards

- Enroll the domain in **Google Postmaster Tools** and **Microsoft SNDS**.
- Confirm domain/IP reputation shows **High/Good** before scaling volume.

### Verification sign-off checklist

- [ ] Single valid SPF record, ends `-all`
- [ ] DKIM verified in ESP, key = 2048-bit
- [ ] DMARC published, reports arriving at `rua` mailbox
- [ ] mail-tester ≥ 9/10 with all three = pass
- [ ] Gmail + Outlook + Yahoo "show original" = all pass
- [ ] Postmaster Tools reputation = High/Good

---

## 10. IP / Domain Warmup (mandatory before bulk volume)

Cold domains sending high volume get throttled. Ramp gradually:

| Day range | Max sends/day |
|---|---|
| 1–3 | 50 |
| 4–7 | 200 |
| 8–14 | 1,000 |
| 15–30 | 5,000 |
| 30+ | Scale by engagement, ~2× every few days |

Prioritize **engaged recipients** early (opens/clicks) — early engagement builds reputation fastest. Keep bounce rate < 2% and spam-complaint rate < 0.1%.

---

## 11. Compliance (non-negotiable for company use)

Every send must satisfy:

- [ ] Valid **physical postal address** in the footer (CAN-SPAM).
- [ ] Working, one-click **unsubscribe** honored within 10 days; add `List-Unsubscribe` + `List-Unsubscribe-Post` headers.
- [ ] **Lawful basis / consent** for marketing recipients (GDPR / India DPDP where applicable).
- [ ] Suppression list enforced — never re-mail an unsubscribe or hard bounce.
- [ ] Accurate `From:`, `Reply-To:`, and subject lines — no deception.

Security must review the first production template and any bulk campaign against this list.

---

## 12. Monitoring & Maintenance

| Cadence | Action |
|---|---|
| Daily | Review bounce + complaint rate in ESP dashboard. |
| Weekly | Parse DMARC aggregate (`rua`) reports (use dmarcian / Postmark DMARC / EasyDMARC). Confirm 100% pass, investigate any unknown source. |
| Monthly | Check Postmaster Tools / SNDS reputation trend. |
| Quarterly | **Rotate DKIM keys** (publish new selector, cut over, retire old). Review SPF includes for stale services. |
| On change | Re-run Section 9 verification after ANY DNS or ESP change. |

---

## 13. Troubleshooting Runbook

| Symptom | Likely cause | Fix |
|---|---|---|
| `dkim=fail` | Message body altered in transit; wrong/rotated key; missing DNS record | Confirm selector record resolves; re-verify in ESP; ensure no relay rewrites body. |
| `spf=fail` | Sending IP not in SPF; >10 DNS lookups; two SPF records | Add ESP `include:`; flatten lookups; merge into single record. |
| `dmarc=fail` but SPF/DKIM pass | **Alignment** failure — `From:` domain ≠ authenticated domain | Set `From:` to the authenticated (sub)domain; check `adkim`/`aspf` mode. |
| Mail lands in spam despite all pass | Reputation / content / no warmup | Complete warmup; check blocklists; review spammy content & links. |
| Sudden deliverability drop | New IP, blocklist hit, spike in complaints | Check SNDS/Postmaster; pause bulk; investigate complaint source in DMARC reports. |

---

## 14. Change Management

- All DNS/ESP changes go through the standard change ticket, reviewed by Infra + DevOps.
- No `p=reject` promotion without two consecutive clean weekly DMARC reports.
- DKIM key rotation follows publish → verify → cutover → retire, never delete-before-verify.

---

## 15. Approval

| Role | Name | Date | Signature |
|---|---|---|---|
| Infra Owner | | | |
| Security | | | |
| Head of Eng | | | |

**Recorded architecture decisions**

| Decision | Choice | Rationale |
|---|---|---|
| ESP vs Self-Host | | |
| Root vs Subdomain | | |

---
*End of SOP OPS-EMAIL-001 v1.1*
