#!/usr/bin/env python3
"""PostToolUse hook — signale les secrets en dur (CLAUDE.md : ❌ secrets en dur, utiliser .env).

Non bloquant : injecte un avertissement dans le contexte de Claude via additionalContext.
Ignore les fichiers d'exemple (.env.example) et les valeurs lues depuis l'environnement.
"""
import json
import re
import sys

# Affectations de type secret = "valeur littérale" (Python, TS/JS, YAML, env).
ASSIGN = re.compile(
    r"""(?ix)
    \b(password|passwd|secret|secret_key|api[_-]?key|access[_-]?key|
       token|auth[_-]?token|private[_-]?key|client[_-]?secret|
       jwt[_-]?secret|db[_-]?password|aws_secret_access_key)\b
    \s*[:=]\s*
    ['"]([^'"\s]{6,})['"]
    """
)

# Motifs de secrets reconnaissables, indépendants du nom de variable.
TOKENS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),                       # AWS access key id
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                    # clés style OpenAI
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),             # tokens GitHub
    re.compile(r"AIza[0-9A-Za-z\-_]{30,}"),                # clés Google/Gemini
]

# Valeurs manifestement non secrètes (lecture d'env, placeholders).
SAFE_VALUE = re.compile(
    r"(?i)(os\.environ|getenv|process\.env|import\.meta\.env|"
    r"\$\{|<.*>|your[_-]|changeme|example|placeholder|xxx+|\*{3,})"
)


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
    if path.endswith((".env.example", ".sample", ".md")):
        sys.exit(0)

    text = new_text(tool_input)
    if not text:
        sys.exit(0)

    hits = []
    for line in text.splitlines():
        if SAFE_VALUE.search(line):
            continue
        if "noqa: secret" in line:
            continue
        m = ASSIGN.search(line)
        if m:
            hits.append(line.strip())
            continue
        if any(tok.search(line) for tok in TOKENS):
            hits.append(line.strip())

    if not hits:
        sys.exit(0)

    preview = "\n".join(f"  • {h}" for h in hits[:5])
    msg = (
        f"⚠️ Secret potentiellement en dur dans {path} — interdit par CLAUDE.md.\n"
        f"{preview}\n"
        "Déplace la valeur dans .env (et documente-la dans .env.example)."
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
