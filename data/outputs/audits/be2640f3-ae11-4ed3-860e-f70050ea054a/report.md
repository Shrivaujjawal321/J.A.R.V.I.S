# Security Audit Report

**Audit ID:** `be2640f3-ae11-4ed3-860e-f70050ea054a`  
**Target:** `/home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd`  
**Generated:** 2026-06-05 12:55 UTC  
**Scanners:** semgrep, trivy, osv, gitleaks, trufflehog

## Summary

| Severity | Count |
|---|---|
| Critical | 3 |
| High | 7 |
| Medium | 9 |
| Low | 18 |
| Info | 0 |

## Top Findings

### 1. [CRITICAL] gitleaks.generic-api-key

**Location:** `/home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd/.env.local` line 1  
**CVSS 4.0:** 9.3  
**CWE:** CWE-798  
**OWASP:** SECRETS  
**Status:** needs_manual  
**Confidence:** 70%  

**Evidence:**
```
Secret detected by rule 'generic-api-key': gf4G...Ipc= (match: AUTH_SECRET=gf4Gn04eBdR0Wu5QtNqCHrM6YAjRxnJaDQI1KuuaIpc=)
```

### 2. [CRITICAL] gitleaks.generic-api-key

**Location:** `/home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd/.env.local` line 19  
**CVSS 4.0:** 9.3  
**CWE:** CWE-798  
**OWASP:** SECRETS  
**Status:** needs_manual  
**Confidence:** 70%  

**Evidence:**
```
Secret detected by rule 'generic-api-key': GOCS...N6cJ (match: AUTH_GOOGLE_SECRET=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)
```

### 3. [CRITICAL] trufflehog.postgres

**Location:** `/home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd/.env.local` line 1  
**CVSS 4.0:** 9.3  
**CWE:** CWE-798  
**OWASP:** SECRETS  
**Status:** needs_manual  
**Confidence:** 70%  

**Evidence:**
```
Detector: Postgres | Secret: post...5432 | (VERIFIED LIVE)
```

### 4. [HIGH] GHSA-267c-6grr-h53f

**CVSS 4.0:** 8.8  
**OWASP:** SCA:CVE  
**Status:** confirmed  
**Confidence:** 85%  

**Evidence:**
```
GHSA-267c-6grr-h53f in next@16.2.4: Next.js has a Middleware / Proxy bypass in App Router applications via segment-prefetch routes
```

**Remediation:** Upgrade `next` to the minimum patched version cited in GHSA-267c-6grr-h53f (check the advisory for the exact safe floor; typically the immediate patch release above 16.2.4). Until the upgrade is applied, add explicit deny rules in your reverse proxy or CDN to block requests whose path matches the segment-prefetch pattern (e.g., `/_next/data/*/` prefetch variants) from bypassing middleware auth checks. After upgrading, audit any App Router middleware performing authentication or authorization to verify it cannot be side-stepped via prefetch-segment route evasion.

### 5. [HIGH] GHSA-26hh-7cqf-hhc6

**CVSS 4.0:** 8.8  
**OWASP:** SCA:CVE  
**Status:** confirmed  
**Confidence:** 85%  

**Evidence:**
```
GHSA-26hh-7cqf-hhc6 in next@16.2.4: Next.js has a Middleware / Proxy bypass in App Router applications via segment-prefetch routes - Incomplete Fix Follow-Up
```

**Remediation:** Upgrade `next` from 16.2.4 to the minimum version listed as fixed in the GHSA-26hh-7cqf-hhc6 advisory (consult https://osv.dev/vulnerability/GHSA-26hh-7cqf-hhc6 for the exact patched release). As mandatory defense-in-depth — regardless of upgrade status — replicate all authentication and authorization logic inside route handlers or server actions and never rely exclusively on App Router middleware, because the segment-prefetch bypass vector can circumvent middleware even on partially-patched releases.

### 6. [HIGH] GHSA-36qx-fr4f-26g5

**CVSS 4.0:** 8.8  
**OWASP:** SCA:CVE  
**Status:** confirmed  
**Confidence:** 85%  

**Evidence:**
```
GHSA-36qx-fr4f-26g5 in next@16.2.4: Next.js has a Middleware / Proxy bypass in Pages Router applications using i18n
```

**Remediation:** Upgrade the `next` package to the minimum patched release in the 16.x line that resolves GHSA-36qx-fr4f-26g5 (consult the advisory's affected-version matrix on osv.dev for the exact floor). If an immediate upgrade is blocked, mitigate by moving all authorization logic behind origin-layer server checks rather than relying solely on Next.js Middleware, and consider temporarily disabling i18n routing in next.config.js until patched. Audit every Middleware-gated route in the Pages Router to confirm no security-sensitive access control can be bypassed via a crafted locale prefix or proxy header.

### 7. [HIGH] GHSA-492v-c6pp-mqqv

**CVSS 4.0:** 8.8  
**OWASP:** SCA:CVE  
**Status:** confirmed  
**Confidence:** 85%  

**Evidence:**
```
GHSA-492v-c6pp-mqqv in next@16.2.4: Next.js has a Middleware / Proxy bypass through dynamic route parameter injection
```

**Remediation:** Upgrade next to the minimum patched version cited in GHSA-492v-c6pp-mqqv (consult https://github.com/advisories/GHSA-492v-c6pp-mqqv for the exact fixed semver range and apply it in package.json, then regenerate the lock file). As an immediate defence-in-depth measure, move all authentication/authorization logic into route handlers or a dedicated server-side session check rather than relying solely on Next.js Middleware, since Middleware-only guards are the exploitable trust boundary. Validate after upgrade that dynamic route segments (e.g. [...slug]) no longer accept injected parameter values that skip middleware execution.

### 8. [HIGH] GHSA-8h8q-6873-q5fj

**CVSS 4.0:** 8.8  
**OWASP:** SCA:CVE  
**Status:** confirmed  
**Confidence:** 85%  

**Evidence:**
```
GHSA-8h8q-6873-q5fj in next@16.2.4: Next.js Vulnerable to Denial of Service with Server Components
```

**Remediation:** Upgrade next from 16.2.4 to the patched version (≥15.3.3 for the 15.x line, or ≥14.2.30 for the 14.x line, per the GHSA advisory). Run `npm install next@latest` or pin to a specific patched release in package.json. If immediate upgrade is not feasible, disable React Server Components or apply the official workaround documented in the advisory to sanitize crafted request headers that trigger the DoS.

### 9. [HIGH] GHSA-mg66-mrh9-m8jx

**CVSS 4.0:** 8.8  
**OWASP:** SCA:CVE  
**Status:** confirmed  
**Confidence:** 85%  

**Evidence:**
```
GHSA-mg66-mrh9-m8jx in next@16.2.4: Next.js vulnerable to Denial of Service via connection exhaustion in applications using Cache Components
```

**Remediation:** Upgrade `next` from 16.2.4 to the earliest patched release resolving GHSA-mg66-mrh9-m8jx (consult the Next.js security advisory for the minimum safe version, typically the immediate patch release ≥16.2.5); update package.json and regenerate the lockfile, then redeploy. If an immediate upgrade is blocked, audit the codebase for any use of Next.js Cache Components (`<unstable_cache>`, `use cache` directive, or equivalent APIs) and disable or feature-flag them to eliminate the connection-exhaustion attack surface until the patch lands.

### 10. [LOW] GHSA-35jp-ww65-95wh

**CVSS 4.0:** 8.8  
**OWASP:** SCA:CVE  
**Status:** confirmed  
**Confidence:** 70%  

**Evidence:**
```
GHSA-35jp-ww65-95wh in axios@1.15.2: axios Vulnerable to Full Man-in-the-Middle via Prototype Pollution Gadget in `config.proxy`
```

---

*Generated by AuditAgent (Jarvis). Defensive-only. Authorized targets only. This report may contain false positives; confirm findings manually before acting.*