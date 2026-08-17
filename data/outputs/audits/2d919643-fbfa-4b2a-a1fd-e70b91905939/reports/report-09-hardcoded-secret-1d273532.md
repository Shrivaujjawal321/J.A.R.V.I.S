# Hardcoded Secret in `....A.R.V.I.S./My Apps/apps/enginerd/.env.local:19` leading to service credential exposure

---

## TL;DR / Summary

A hardcoded credential or secret key was found at `/home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd/.env.local:19`. The value sits in plaintext on disk. The file is NOT currently git-tracked (e.g. a local/gitignored env file), so exposure depends on whether it was ever committed (verify in step 2) or shipped in a build/artifact — but a plaintext credential is still a rotation-worthy exposure.

---

## Severity

- **CVSS v4.0 vector:** `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N`
- **Rating / Score:** Critical (7.5)
- **Why this severity:** AV:N, AC:L, PR:N — the credential is accessible to anyone with repo read access. VC:H/VI:H because the associated service is fully compromised once the key is used. Computed vector: `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N`.

---

## Vulnerability Details

- **Type:** Hardcoded Secret
- **CWE:** CWE-798
- **OWASP:** SECRETS

---

## Affected Asset

- **File / Component:** `/home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd/.env.local:19`
- **Target:** `/home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd`
- **Audit ID:** `2d919643-fbfa-4b2a-a1fd-e70b91905939`

---

## Description (Bug + Root Cause)

A hardcoded credential or secret key was found at `/home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd/.env.local:19`. The value sits in plaintext on disk. The file is NOT currently git-tracked (e.g. a local/gitignored env file), so exposure depends on whether it was ever committed (verify in step 2) or shipped in a build/artifact — but a plaintext credential is still a rotation-worthy exposure.

---

## Steps to Reproduce

> Deterministic, numbered, copy-pasteable. A triager with zero context must reproduce on the first try.

1. Confirm the secret is present at `/home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd/.env.local:19` (scanner: gitleaks, rule: gitleaks.generic-api-key).
2. Verify the secret is committed to version history: `git log --all -p -- /home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd/.env.local | grep AUTH...C`
3. Identify which service or system the credential authenticates against (infer from surrounding code or key prefix).
4. Perform a benign identity check to confirm the credential is currently active:
5.     AWS key: `aws sts get-caller-identity` (do not access resources).
6.     Generic token: a read-only API call (e.g. GET /user or /me endpoint).
7. Document: the key is valid, whether it is committed to history, and the associated service.
8. Expected: credentials managed via environment variables or a secrets manager. Actual: plaintext credential in source code.
9. IMPORTANT: do not use the credential beyond the identity check. Report and rotate immediately.

---

## Proof of Concept

**Location:** `/home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd/.env.local:19`
**Scanner:** gitleaks  |  **Rule:** gitleaks.generic-api-key

**Masked secret value:**
```
AUTH...CRET
```

**Evidence (masked):**
```
Secret detected by rule 'generic-api-key': GOCS...N6cJ (match: AUTH...CRET=GOCS...N6cJ)
```

**Git history confirmation:**
```bash
git log --all -p -- /home/ujjwal/Documents/J.A.R.V.I.S./My Apps/apps/enginerd/.env.local
```

**Confirm active credential (benign identity check only):**
```bash
# Example for AWS — identity echo, no resource access
AWS_ACCESS_KEY_ID=<key> AWS_SECRET_ACCESS_KEY=<secret> aws sts get-caller-identity
```

Do NOT use the credential to access, modify, or exfiltrate data.
Full secret value is withheld from this report; rotate immediately upon triage.


> Defensive / authorized testing only. PoC is designed to confirm the vulnerability for the asset owner's triager. All secret values are masked. No weaponized payloads.

---

## Impact / Business Impact

Any party with repository read access — including collaborators, CI/CD systems, and anyone who has cloned or forked the repo — holds the credential. The associated service is fully compromised until the credential is rotated. Historical Git commits preserve the secret even after file deletion.

---

## Remediation / Recommended Fix

**Primary fix:** Immediately rotate the exposed credential. Remove the hardcoded value and replace with an environment variable or secret manager reference (e.g. AWS Secrets Manager, Vault, Doppler). Purge the secret from Git history using `git filter-repo` or BFG Repo Cleaner.

**Defense-in-depth:** Add a pre-commit hook (`gitleaks` or `detect-secrets`) to block future secret commits. Configure your CI/CD pipeline to fail on secret detection (GitHub Advanced Security / GitLab Secret Detection). Audit all forks and clones to determine exposure scope.

---

## References

- https://cwe.mitre.org/data/definitions/798.html
- https://cwe.mitre.org/data/definitions/259.html
- https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure
- https://trufflesecurity.com/blog/trufflehog-detectors

---

*Generated by AuditAgent (Jarvis). Defensive-only. Authorized targets only.*  
*Platform hint: HackerOne / Bugcrowd — check the program's asset list for the affected repo*  
*Generated: 2026-06-06 03:57 UTC*  
*LLM-enriched: False*