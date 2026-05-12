"""
Scout-and-fill helpers for the browser-autopilot skill.

The pattern: before any form action, snapshot the page's accessibility tree,
match logical field labels to UIDs, build a fill plan, validate it has enough
coverage, and only THEN execute. Survives DOM cosmetic changes because we use
ARIA roles + labels (semantic), not CSS selectors (structural).

Note: the snapshot parsing here is intentionally generic and tolerant — different
Chrome DevTools MCP server versions return slightly different node shapes. The
matcher functions accept dict-like nodes with these common keys:
- uid / nodeId / id        — opaque ID to pass back to MCP tools
- role / aria-role         — semantic role (button, textbox, combobox, etc.)
- name / label / aria-label / text  — human-readable label
- required / aria-required — required flag (any truthy variant)
- type                     — input type (text, email, file, password, ...)
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger("browser_autopilot.scout")


# === Data classes ===


@dataclass
class FieldSpec:
    """One field in a fill plan."""

    label: str                  # The logical name (e.g. "Phone Number")
    uid: str                    # MCP UID for click/fill operations
    field_type: str             # text / email / tel / file / select / combobox / radio / checkbox / textarea
    required: bool = False
    aria_role: str | None = None
    aria_label: str | None = None
    matched_via: str = "unknown"  # "exact_label" | "substring" | "type_only" | etc.


@dataclass
class FillPlan:
    """Full plan: which fields to fill, with what values."""

    form_url: str
    fields: list[FieldSpec] = field(default_factory=list)
    file_uploads: list[tuple[FieldSpec, str]] = field(default_factory=list)
    submit_button_uid: str | None = None
    submit_button_label: str | None = None
    unmatched_inputs: list[str] = field(default_factory=list)  # labels requested but not found
    coverage_ratio: float = 1.0   # matched / requested

    def is_executable(self, min_coverage: float = 0.7) -> bool:
        """True if enough fields matched to safely execute."""
        return self.coverage_ratio >= min_coverage


# === Snapshot parsing ===


_INTERACTIVE_ROLES = {
    "button", "link", "textbox", "searchbox", "combobox", "listbox",
    "checkbox", "radio", "switch", "slider", "menuitem", "tab",
    "spinbutton",
}


def _norm(s: str | None) -> str:
    """Lowercase + collapse whitespace for label matching."""
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip().lower()


def _node_label(node: dict[str, Any]) -> str:
    """Extract the best human-readable label from a snapshot node."""
    for key in ("aria-label", "ariaLabel", "label", "name", "text", "innerText", "title"):
        val = node.get(key)
        if val:
            return str(val)
    # Look in nested labelledby / description fields
    for key in ("ariaLabelledBy", "ariaDescribedBy"):
        val = node.get(key)
        if val and isinstance(val, list) and val:
            return str(val[0])
    return ""


def _node_uid(node: dict[str, Any]) -> str | None:
    for key in ("uid", "nodeId", "id", "backendDOMNodeId"):
        val = node.get(key)
        if val is not None:
            return str(val)
    return None


def _node_type(node: dict[str, Any]) -> str:
    """Derive a field-type token from role + html attrs."""
    role = _norm(node.get("role") or node.get("ariaRole"))
    if role in ("textbox", "searchbox"):
        # Inspect underlying input type if present
        t = _norm(node.get("type") or node.get("inputType"))
        return t or "text"
    if role == "combobox":
        return "combobox"
    if role == "listbox":
        return "listbox"
    if role == "checkbox":
        return "checkbox"
    if role == "radio":
        return "radio"
    if role == "switch":
        return "switch"
    if role == "button":
        return "button"
    # File inputs are typically role=button with hidden file input — caller handles
    return role or "unknown"


def _is_required(node: dict[str, Any]) -> bool:
    for key in ("required", "aria-required", "ariaRequired"):
        val = node.get(key)
        if val is True or _norm(str(val)) in ("true", "yes", "1"):
            return True
    return False


def walk_nodes(snapshot: Any) -> list[dict[str, Any]]:
    """Flatten a snapshot to a list of dict nodes. Tolerant of multiple shapes.

    Accepted inputs:
    - list of dicts (each dict is a node, optionally with 'children'/'nodes' keys)
    - dict tree (with 'children'/'nodes' for recursion)
    - **str** — Chrome DevTools MCP text snapshot (uid=X role "name" key=val ...)
    """
    if isinstance(snapshot, str):
        return parse_text_snapshot(snapshot)
    if isinstance(snapshot, list):
        out = []
        for item in snapshot:
            out.extend(walk_nodes(item))
        return out
    if isinstance(snapshot, dict):
        result = [snapshot]
        for key in ("children", "nodes", "subtree"):
            kids = snapshot.get(key)
            if kids:
                result.extend(walk_nodes(kids))
        return result
    return []


# === Chrome DevTools MCP text-snapshot parser ===
#
# Format (one node per line):
#   uid=1_16 combobox "Search" autocomplete="both" expandable focusable haspopup="listbox"
#
# Tokens after uid+role+name are either:
#   - flags (single word, e.g. `required`, `expandable`, `disabled`)
#   - key="value" attributes
#   - key=value attributes (rare but seen)


_LINE_RE = re.compile(
    r"""^\s*
        uid=(?P<uid>\S+)\s+
        (?P<role>\S+)
        (?:\s+"(?P<name>[^"]*)")?
        (?P<rest>.*)$
    """,
    re.VERBOSE,
)
_ATTR_RE = re.compile(r'(\w[\w-]*)=(?:"([^"]*)"|(\S+))')
_FLAG_RE = re.compile(r"\b(required|expandable|focusable|focused|disabled|selected|checked|haspopup)\b")


def parse_text_snapshot(text: str) -> list[dict[str, Any]]:
    """Parse Chrome DevTools MCP's text snapshot into a list of dict nodes.

    Returns nodes in document order. Each node:
      {
        "uid":     "1_16",
        "role":    "combobox",
        "name":    "Search",
        "<attrs>": <values>,
        "<flags>": True,
      }
    """
    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        # Skip header lines and empty lines
        if not line.strip() or line.lstrip().startswith("#") or line.lstrip().startswith("##"):
            continue
        m = _LINE_RE.match(line)
        if not m:
            continue
        node: dict[str, Any] = {
            "uid": m.group("uid"),
            "role": m.group("role"),
        }
        name = m.group("name")
        if name is not None:
            node["name"] = name
        rest = m.group("rest") or ""
        # Pull key="value" or key=value attributes
        for attr_m in _ATTR_RE.finditer(rest):
            key = attr_m.group(1)
            val = attr_m.group(2) if attr_m.group(2) is not None else attr_m.group(3)
            node[key] = val
        # Pull boolean flags (don't double-count keys already captured)
        # Trim out portions that were attr matches
        attr_spans = [m.span() for m in _ATTR_RE.finditer(rest)]
        if attr_spans:
            # Remove attr substrings from `rest` for flag scanning
            chars = list(rest)
            for start, end in attr_spans:
                for i in range(start, end):
                    chars[i] = " "
            flag_text = "".join(chars)
        else:
            flag_text = rest
        for flag_m in _FLAG_RE.finditer(flag_text):
            node[flag_m.group(1)] = True
        out.append(node)
    return out


def find_interactive_nodes(snapshot: Any) -> list[dict[str, Any]]:
    """Filter to interactive form-like elements."""
    out = []
    for node in walk_nodes(snapshot):
        role = _norm(node.get("role") or node.get("ariaRole"))
        if role in _INTERACTIVE_ROLES:
            out.append(node)
    return out


# === Matching ===


def match_field(target_label: str, candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str]:
    """Find the best snapshot node for a logical field label.

    Returns (node, matched_via). Strategies in order:
      1. Exact (case-insensitive) match on aria-label / label / name
      2. Substring match — target inside candidate label
      3. Substring match — candidate label inside target
      4. Heuristic: known label aliases (e.g. "phone" -> "phone number" / "mobile")
    """
    target_norm = _norm(target_label)
    if not target_norm:
        return None, "empty_target"

    # 1. Exact
    for node in candidates:
        if _norm(_node_label(node)) == target_norm:
            return node, "exact_label"

    # 2. Target inside candidate
    for node in candidates:
        lbl = _norm(_node_label(node))
        if lbl and target_norm in lbl:
            return node, "substring_in_candidate"

    # 3. Candidate inside target
    for node in candidates:
        lbl = _norm(_node_label(node))
        if lbl and lbl in target_norm and len(lbl) >= 3:
            return node, "candidate_in_substring"

    # 4. Heuristic aliases
    aliases = _label_aliases(target_norm)
    for alias in aliases:
        for node in candidates:
            lbl = _norm(_node_label(node))
            if alias in lbl or lbl in alias:
                return node, f"alias:{alias}"

    return None, "no_match"


_ALIAS_MAP: dict[str, list[str]] = {
    "phone": ["phone number", "mobile", "contact number", "phone no", "cell"],
    "email": ["email address", "e-mail", "email id"],
    "resume": ["resume", "cv", "curriculum vitae", "upload resume", "attach resume", "attach cv"],
    "cover letter": ["cover letter", "additional information", "additional info", "message", "note to recruiter"],
    "experience": ["years of experience", "total experience", "yoe", "work experience"],
    "salary": ["expected salary", "salary expectation", "compensation", "ctc"],
    "current salary": ["current ctc", "present salary", "current compensation"],
    "notice period": ["notice period", "availability", "joining date"],
    "location": ["current location", "location", "city"],
}


def _label_aliases(target_norm: str) -> list[str]:
    """Find alias terms for a target label."""
    for key, aliases in _ALIAS_MAP.items():
        if target_norm == key or any(target_norm in a or a in target_norm for a in aliases):
            return [key] + aliases
    return []


# === Plan builder ===


def build_fill_plan(
    *,
    form_url: str,
    snapshot: Any,
    requested_fields: dict[str, str],
    file_field_map: dict[str, str] | None = None,
    submit_button_text_hints: list[str] | None = None,
) -> FillPlan:
    """Build a FillPlan from a snapshot.

    Args:
        form_url: The page URL (for the plan record).
        snapshot: The result of take_snapshot — tree or list of nodes.
        requested_fields: Logical field name -> value to fill.
        file_field_map: Logical field name -> file path on disk.
        submit_button_text_hints: Substring matches to identify the submit button
            (e.g. ["submit application", "apply", "next", "continue"]).

    Returns:
        FillPlan with fields, file_uploads, submit_button_uid populated.
    """
    file_field_map = file_field_map or {}
    submit_button_text_hints = submit_button_text_hints or [
        "submit application",
        "submit",
        "next",
        "continue",
        "review your application",
    ]

    interactive = find_interactive_nodes(snapshot)
    plan = FillPlan(form_url=form_url)

    # Match text/select/combo fields
    requested_total = len(requested_fields) + len(file_field_map)
    matched_count = 0

    for label, value in requested_fields.items():
        node, how = match_field(label, interactive)
        if node is None:
            plan.unmatched_inputs.append(label)
            log.warning("No match for field %r at %s", label, form_url)
            continue
        uid = _node_uid(node)
        if uid is None:
            plan.unmatched_inputs.append(label)
            continue
        spec = FieldSpec(
            label=label,
            uid=uid,
            field_type=_node_type(node),
            required=_is_required(node),
            aria_role=_norm(node.get("role") or node.get("ariaRole")) or None,
            aria_label=_node_label(node) or None,
            matched_via=how,
        )
        plan.fields.append(spec)
        matched_count += 1

    # Match file uploads
    for label, filepath in file_field_map.items():
        node, how = match_field(label, interactive)
        if node is None:
            plan.unmatched_inputs.append(label)
            continue
        uid = _node_uid(node)
        if uid is None:
            plan.unmatched_inputs.append(label)
            continue
        spec = FieldSpec(
            label=label,
            uid=uid,
            field_type="file",
            required=_is_required(node),
            aria_label=_node_label(node) or None,
            matched_via=how,
        )
        plan.file_uploads.append((spec, filepath))
        matched_count += 1

    # Identify submit button
    for hint in submit_button_text_hints:
        hint_norm = _norm(hint)
        for node in interactive:
            role = _norm(node.get("role") or node.get("ariaRole"))
            if role != "button":
                continue
            lbl = _norm(_node_label(node))
            if hint_norm in lbl:
                plan.submit_button_uid = _node_uid(node)
                plan.submit_button_label = _node_label(node)
                break
        if plan.submit_button_uid:
            break

    plan.coverage_ratio = (matched_count / requested_total) if requested_total else 1.0
    return plan


# === Validation helpers ===


def find_validation_errors(snapshot: Any) -> list[str]:
    """Walk snapshot for ARIA-flagged error messages."""
    errors: list[str] = []
    for node in walk_nodes(snapshot):
        role = _norm(node.get("role") or node.get("ariaRole"))
        if role in ("alert", "alertdialog"):
            txt = _node_label(node)
            if txt:
                errors.append(txt)
        # aria-invalid="true" inputs
        invalid = node.get("aria-invalid") or node.get("ariaInvalid")
        if str(invalid).lower() in ("true", "1"):
            lbl = _node_label(node)
            errors.append(f"Invalid field: {lbl or _node_uid(node)}")
    return errors


def find_captcha(snapshot: Any) -> bool:
    """Detect common CAPTCHA / verify-human signals in a snapshot."""
    text_blob = " ".join(_norm(_node_label(n)) for n in walk_nodes(snapshot))
    captcha_terms = [
        "recaptcha",
        "verify you're human",
        "verify you are human",
        "security check",
        "are you a robot",
        "i'm not a robot",
        "hcaptcha",
        "cloudflare verify",
    ]
    return any(term in text_blob for term in captcha_terms)


# === Sanity self-test (no MCP calls — exercises the parsing logic) ===


def _self_test() -> None:
    # --- Test 1: JSON-shape snapshot (legacy) ---
    fake_snapshot = [
        {"role": "textbox", "name": "Phone Number", "uid": "n1", "type": "tel", "required": True},
        {"role": "textbox", "name": "Years of Experience", "uid": "n2", "required": True},
        {"role": "button", "name": "Submit Application", "uid": "n3"},
        {"role": "textbox", "name": "Email address", "uid": "n4", "type": "email"},
        {"role": "button", "name": "Upload Resume", "uid": "n5"},
    ]
    plan = build_fill_plan(
        form_url="https://test/job",
        snapshot=fake_snapshot,
        requested_fields={
            "Phone Number": "+91999",
            "Email": "boss@example.com",
            "Experience": "1",
        },
        file_field_map={"Resume": "/tmp/resume.pdf"},
    )
    assert plan.coverage_ratio == 1.0, f"coverage_ratio={plan.coverage_ratio}"
    assert plan.submit_button_uid == "n3"
    assert len(plan.fields) == 3
    assert len(plan.file_uploads) == 1
    assert plan.unmatched_inputs == []
    print("scout_and_fill JSON-snapshot test: PASS")

    # --- Test 2: real Chrome DevTools MCP text snapshot ---
    real_snapshot_text = """## Latest page snapshot
uid=1_0 RootWebArea "Google" url="https://www.google.com/"
  uid=1_14 search
    uid=1_15 button "Upload files or images" haspopup="menu"
    uid=1_16 combobox "Search" autocomplete="both" expandable focusable focused haspopup="listbox"
    uid=1_21 button "Google Search" description="Google Search"
"""
    nodes = parse_text_snapshot(real_snapshot_text)
    assert len(nodes) == 5, f"expected 5 nodes, got {len(nodes)}: {nodes}"
    search_combo = next(n for n in nodes if n["uid"] == "1_16")
    assert search_combo["role"] == "combobox", search_combo
    assert search_combo["name"] == "Search", search_combo
    assert search_combo.get("autocomplete") == "both", search_combo
    assert search_combo.get("focused") is True, search_combo
    print("scout_and_fill text-snapshot parser: PASS")

    # --- Test 3: build_fill_plan over a text snapshot ---
    plan2 = build_fill_plan(
        form_url="https://www.google.com/",
        snapshot=real_snapshot_text,
        requested_fields={"Search": "Jarvis super agent"},
        submit_button_text_hints=["google search"],
    )
    assert plan2.coverage_ratio == 1.0, f"coverage={plan2.coverage_ratio}"
    assert len(plan2.fields) == 1
    assert plan2.fields[0].uid == "1_16"
    assert plan2.submit_button_uid == "1_21"
    print("scout_and_fill end-to-end (text snapshot → plan): PASS")


if __name__ == "__main__":
    _self_test()
