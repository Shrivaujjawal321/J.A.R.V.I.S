"""
Post-on-Vercel-deploy hook for the LinkedIn pipeline.

Called by .github/workflows/post-on-deploy.yml after a successful Vercel deploy.
Drafts a project-showcase LinkedIn post for the deployed project and queues it
into TOMORROW's morning batch (NEVER auto-publishes).

CLI:
    python -m scripts.linkedin.post_on_deploy \
        --project-name "JarvisChat" \
        --vercel-url "https://jarvischat.vercel.app" \
        --repo "github.com/Shrivaujjawal321/jarvis-chat" \
        --commit-sha "abc1234" \
        --readme-path "README.md"

Output:
    Drafts a JSON file in data/linkedin/posts/queued/<timestamp>_<project>.json
    that the next morning_runner will pick up to override Tuesday's slot.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from . import _claude_helper, _telegram_notify

JARVIS_ROOT = Path(__file__).resolve().parents[2]
QUEUE_DIR = JARVIS_ROOT / "data" / "linkedin" / "posts" / "queued"


DEPLOY_POST_PROMPT = """\
You are drafting a LinkedIn post for Ujjawal Shrivastav announcing a freshly
deployed project.

## Project context
- Name: {name}
- Live URL: {vercel_url}
- Repo: {repo}
- Latest commit SHA: {commit_sha}

## README excerpt (truncated)
{readme}

## Voice rules
- Hook in first 2 lines: lead with WHAT it does + WHO it's for, in <150 chars.
- NO "thrilled to announce". NO "I built this".
- Open with the problem or the surprising thing about how it works.
- Body: 3 short paragraphs max — what / how (one technical detail) / what's next.
- Include the live URL once and the repo URL once.
- 800-1500 chars total.
- 3-5 niche hashtags at the end.
- CTA: ask for one specific kind of feedback (not "thoughts?").

Reply with ONLY this JSON:
{{
  "post": "<full post text including hashtags>",
  "char_count": <int>,
  "hook": "<first 2 lines>",
  "cta": "<the CTA line>"
}}
"""


def _trim_readme(path: Path | None, max_chars: int = 3500) -> str:
    if not path or not path.exists():
        return "(README not provided)"
    txt = path.read_text(encoding="utf-8", errors="ignore")
    return txt[:max_chars]


def queue_for_next_morning(
    *,
    name: str,
    vercel_url: str,
    repo: str,
    commit_sha: str,
    readme_path: str | None = None,
) -> Path:
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    readme = _trim_readme(Path(readme_path) if readme_path else None)
    prompt = DEPLOY_POST_PROMPT.format(
        name=name,
        vercel_url=vercel_url,
        repo=repo,
        commit_sha=commit_sha,
        readme=readme,
    )
    drafted = _claude_helper.json_call(prompt)
    payload = {
        "kind": "deploy-post",
        "queued_at": datetime.now(timezone.utc).isoformat(),
        "project": {
            "name": name,
            "vercel_url": vercel_url,
            "repo": repo,
            "commit_sha": commit_sha,
        },
        "draft": drafted,
        "consumed": False,
    }
    fname = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"_{name.replace(' ', '_')}.json"
    out_path = QUEUE_DIR / fname
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    _telegram_notify.send(
        f"🚀 *Vercel deploy detected — {name}*\n"
        f"Live: {vercel_url}\n"
        f"Drafted LinkedIn post queued for tomorrow's morning batch.\n"
        f"Preview: `{drafted.get('hook', '')}`\n"
        f"(File: `{out_path.name}`)"
    )
    return out_path


def main() -> None:
    p = argparse.ArgumentParser(prog="linkedin.post_on_deploy")
    p.add_argument("--project-name", required=True)
    p.add_argument("--vercel-url", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--commit-sha", required=True)
    p.add_argument("--readme-path")
    args = p.parse_args()
    out = queue_for_next_morning(
        name=args.project_name,
        vercel_url=args.vercel_url,
        repo=args.repo,
        commit_sha=args.commit_sha,
        readme_path=args.readme_path,
    )
    print(f"Queued: {out}")


if __name__ == "__main__":
    main()
