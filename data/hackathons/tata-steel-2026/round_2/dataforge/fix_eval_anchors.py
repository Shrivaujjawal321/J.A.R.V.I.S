"""
UI-NEW-2 fix: make every eval grounding_ref of the form `file.md#anchor` resolve to a
REAL heading under one canonical GitHub slug rule. For each ref we match the anchor to
the document's actual headings (tolerant alnum match), rewrite to the heading's canonical
github slug, or drop to file-level if no heading matches. Non-md refs (spine:/incident:/
run:/rca:/asset ids) are left as-is. Reports before/after resolve rate.
"""
import json, re
from pathlib import Path

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship")
KD = BASE/"knowledge_docs"
UI = BASE/"user_interaction"

def gh_slug(h):
    h = h.strip().lower()
    h = re.sub(r"[^\w\s-]", "", h)     # keep word chars (incl _), space, hyphen
    h = re.sub(r"\s+", "-", h)
    return h
def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

# build heading slug maps for every markdown doc (basename -> {canonical_slug, norm->slug})
slugmap = {}     # filename -> set of canonical slugs
normmap = {}     # filename -> { norm(slug): canonical_slug }
for md in KD.rglob("*.md"):
    slugs = []
    for line in md.read_text(errors="ignore").splitlines():
        m = re.match(r"^#{1,6}\s+(.*)", line)
        if m:
            s = gh_slug(m.group(1))
            if s: slugs.append(s)
    slugmap[md.name] = set(slugs)
    normmap[md.name] = {norm(s): s for s in slugs}

def resolve_ref(ref):
    """Return (fixed_ref, status) where status in keep/fixed/file-level/nonmd."""
    if "#" not in ref:
        return ref, "nonmd-or-file"
    left, anchor = ref.split("#", 1)
    fname = left.split("/")[-1]
    if not fname.endswith(".md"):
        return ref, "nonmd"          # spine:..#tag style — leave
    if fname not in slugmap:
        return left, "file-level(no-doc)"
    a_can = gh_slug(anchor)
    if a_can in slugmap[fname]:
        return f"{left}#{a_can}", "keep" if a_can == anchor else "fixed"
    na = norm(anchor)
    if na in normmap[fname]:
        return f"{left}#{normmap[fname][na]}", "fixed"
    # prefix / containment match
    cands = [s for k, s in normmap[fname].items() if k.startswith(na) or na.startswith(k) or na in k]
    if len(cands) >= 1:
        cands.sort(key=lambda s: abs(len(norm(s))-len(na)))
        return f"{left}#{cands[0]}", "fixed"
    return left, "file-level(no-heading)"

stats = {"keep":0,"fixed":0,"file-level(no-heading)":0,"file-level(no-doc)":0,"nonmd":0,"nonmd-or-file":0}
def fix_obj_refs(obj):
    changed = False
    refs = obj.get("grounding_refs")
    if isinstance(refs, list):
        new = []
        for r in refs:
            fr, st = resolve_ref(str(r))
            stats[st] = stats.get(st,0)+1
            if fr != r: changed = True
            new.append(fr)
        # dedupe preserve order
        seen=set(); dd=[x for x in new if not (x in seen or seen.add(x))]
        obj["grounding_refs"] = dd
    return changed

for fn in ["nl_queries.jsonl","troubleshooting_prompts.jsonl","multiturn_conversations.jsonl"]:
    p = UI/fn
    if not p.exists(): continue
    out=[]; nch=0
    for line in p.read_text().splitlines():
        if not line.strip(): continue
        o=json.loads(line)
        if fix_obj_refs(o): nch+=1
        out.append(json.dumps(o, ensure_ascii=False))
    p.write_text("\n".join(out)+"\n")
    print(f"{fn}: {len(out)} records, {nch} had refs rewritten")

md_total = sum(v for k,v in stats.items() if not k.startswith("nonmd"))
resolved = stats["keep"]+stats["fixed"]
print("\nmd#anchor refs:", md_total, "| keep:", stats["keep"], "fixed:", stats["fixed"],
      "dropped-to-file:", stats["file-level(no-heading)"]+stats["file-level(no-doc)"])
print(f"resolve rate after fix: {100*resolved/max(md_total,1):.1f}% resolve to a real heading; rest are clean file-level")
print("non-md (spine/incident/run/rca/id) refs left as-is:", stats["nonmd"]+stats["nonmd-or-file"])
