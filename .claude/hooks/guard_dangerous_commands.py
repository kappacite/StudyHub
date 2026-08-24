#!/usr/bin/env python3
"""PreToolUse hook (Bash|PowerShell) — bloque les commandes destructrices.

Bloquant : git push, git reset --hard, git rebase, rm -rf / Remove-Item -Recurse
-Force, docker compose down -v/--volumes, ./deploy.sh, flask db upgrade en
direct, et toute commande contenant une chaine ressemblant a une cle API.
Complete (ne remplace pas) le bloc "deny" de settings.json : les regex ici
attrapent les variantes d'arguments qu'un simple prefixe glob peut manquer.
"""
import json
import re
import sys

RULES = [
    (re.compile(r"(^|[;&|]|\n)\s*git\s+push\b"), "git push est interdit en toute circonstance."),
    (re.compile(r"(^|[;&|]|\n)\s*git\s+reset\s+--hard\b"), "git reset --hard est interdit."),
    (re.compile(r"(^|[;&|]|\n)\s*git\s+rebase\b"), "git rebase est interdit."),
    (re.compile(r"(^|[;&|]|\n)\s*rm\s+(-\w*r\w*f\w*|-\w*f\w*r\w*)\s"), "rm -rf est interdit."),
    (re.compile(r"Remove-Item\s+.*-Recurse\b.*-Force\b|Remove-Item\s+.*-Force\b.*-Recurse\b", re.I), "Remove-Item -Recurse -Force est interdit."),
    (re.compile(r"docker\s+compose\s+down\s+.*(-v\b|--volumes\b)", re.I), "docker compose down -v/--volumes est interdit (destruction de volumes)."),
    (re.compile(r"(^|[;&|/\\]|\n)\s*(\./)?deploy\.sh\b"), "deploy.sh execute une migration flask db upgrade en production directe — interdit sans confirmation explicite."),
    (re.compile(r"flask\s+db\s+upgrade\b"), "flask db upgrade en direct est interdit hors dev (auto-migration au demarrage s'en charge)."),
]

TOKEN_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{30,}"),
]


HEREDOC_START = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")


def strip_heredocs(command: str) -> str:
    """Retire le corps des heredocs (ex. git commit -m "$(cat <<'EOF' ... EOF)")
    avant l'analyse : c'est du texte litteral (message de commit, contenu de
    fichier), pas des commandes shell executees — le mentionner ne doit pas
    declencher les regles ci-dessous."""
    out = []
    pos = 0
    for m in HEREDOC_START.finditer(command):
        delim = m.group(2)
        out.append(command[pos:m.end()])
        body_start = command.find("\n", m.end())
        if body_start == -1:
            pos = m.end()
            continue
        body_start += 1
        end_re = re.compile(rf"^\s*{re.escape(delim)}\s*$", re.M)
        end_match = end_re.search(command, body_start)
        if end_match:
            out.append("\n<heredoc omis>\n")
            pos = end_match.end()
        else:
            out.append(command[body_start:])
            pos = len(command)
    out.append(command[pos:])
    return "".join(out)


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        sys.exit(0)

    command = (payload.get("tool_input", {}) or {}).get("command", "") or ""
    if not command:
        sys.exit(0)

    command = strip_heredocs(command)

    for pattern, reason in RULES:
        if pattern.search(command):
            deny(f"⛔ Commande bloquee (guard_dangerous_commands) : {reason}")

    for pattern in TOKEN_PATTERNS:
        if pattern.search(command):
            deny(
                "⛔ Commande bloquee (guard_dangerous_commands) : la commande "
                "contient une chaine ressemblant a une cle/API secrete en clair."
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
