#!/usr/bin/env python3
"""PostToolUse hook — signale les traces de debug oubliées (CLAUDE.md : ❌ console.log / print de debug).

Non bloquant : injecte un avertissement dans le contexte de Claude via additionalContext.
Cible les sources applicatives uniquement (pas les tests/scripts/migrations où print est légitime).
"""
import json
import re
import sys

# (regex de détection, prédicat sur le chemin)
PY_DEBUG = re.compile(r"(^|[^.\w])print\s*\(")
JS_DEBUG = re.compile(r"console\.(log|debug|trace)\s*\(")


def is_python_src(path: str) -> bool:
    return (
        path.endswith(".py")
        and "/backend/app/" in path
        and "/tests/" not in path
        and "/scripts/" not in path
        and "/scratch/" not in path
        and "/migrations/" not in path
    )


def is_web_src(path: str) -> bool:
    return "/web/src/" in path and path.endswith((".ts", ".js", ".vue"))


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
    text = new_text(tool_input)
    if not text:
        sys.exit(0)

    if is_python_src(path):
        pattern, label = PY_DEBUG, "print(...)"
    elif is_web_src(path):
        pattern, label = JS_DEBUG, "console.log/debug/trace(...)"
    else:
        sys.exit(0)

    hits = [
        line.strip()
        for line in text.splitlines()
        if pattern.search(line) and "noqa: debug" not in line
    ]
    if not hits:
        sys.exit(0)

    preview = "\n".join(f"  • {h}" for h in hits[:5])
    msg = (
        f"⚠️ Trace de debug détectée dans {path} ({label}) — interdit par CLAUDE.md.\n"
        f"{preview}\n"
        "Retire-la (ou utilise un vrai logger) avant de committer."
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": msg,
                }
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
