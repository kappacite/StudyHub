#!/usr/bin/env python3
"""PostToolUse hook — signale les valeurs de style brutes dans les primitives UI
(CLAUDE.md : #rrggbb / rgb(...) / px hors 0-1px / classe Tailwind arbitraire [...] interdits).

Non bloquant : injecte un avertissement dans le contexte de Claude via additionalContext.
Cible uniquement web/src/components/ui/ (primitives) — le reste de l'app n'est pas encore
migre vers Direction A (phase 4, skill migration-ecran) et peut legitimement contenir des
valeurs non tokenisees jusqu'a sa migration ecran par ecran.
"""
import json
import re
import sys

HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
RGB_FUNC = re.compile(r"\brgba?\(\s*\d")
ARBITRARY_TAILWIND = re.compile(
    r"\b(?:bg|text|border|shadow|rounded|w|h|p|m|gap|top|left|right|bottom|inset)-\[[^\]]+\]"
)
RAW_PX = re.compile(r"\b(?:[2-9]|\d{2,})px\b")


def is_ui_primitive(path: str) -> bool:
    norm = path.replace("\\", "/")
    # Match both absolute and relative paths that contain web/src/components/ui/
    return (("web/src/components/ui/" in norm or "/web/src/components/ui/" in norm)
            and norm.endswith(".vue"))


def new_text(tool_input: dict) -> str:
    parts = []
    if "content" in tool_input:
        parts.append(tool_input["content"])
    if "new_string" in tool_input:
        parts.append(tool_input["new_string"])
    for edit in tool_input.get("edits", []) or []:
        if isinstance(edit, dict) and "new_string" in edit:
            parts.append(edit["new_string"])
    return "\n".join(p for p in parts if isinstance(p, str))


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    tool_input = payload.get("tool_input", {}) or {}
    path = tool_input.get("file_path", "") or ""
    if not is_ui_primitive(path):
        sys.exit(0)

    text = new_text(tool_input)
    if not text:
        sys.exit(0)

    hits = []
    for line in text.splitlines():
        stripped = line.strip()
        if (HEX_COLOR.search(stripped) or RGB_FUNC.search(stripped)
                or ARBITRARY_TAILWIND.search(stripped) or RAW_PX.search(stripped)):
            hits.append(stripped)

    if not hits:
        sys.exit(0)

    preview = "\n".join(f"  • {h}" for h in hits[:5])
    msg = (
        f"⚠️ Valeur de style brute détectée dans {path} — interdit sur une primitive "
        f"(CLAUDE.md : #rrggbb / rgb(...) / px hors 0-1px / classe Tailwind arbitraire).\n"
        f"{preview}\n"
        "Remplace par un token (couleur sémantique, rounded-*, text-*, espacement standard)."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
