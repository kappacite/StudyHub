#!/usr/bin/env python3
"""PostToolUse hook (Write|Edit|MultiEdit) — formatage auto du frontend web.

Sur tout fichier web/**.{vue,ts,js} touche : `eslint --fix` puis
`prettier --write`, non bloquant. Ajoute ensuite un avertissement (non
bloquant) si le fichier contient une valeur de style brute (#rrggbb, rgb(),
px hors 0px/1px) au lieu d'un token — CLAUDE.md l'interdit.
"""
import json
import pathlib
import re
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parents[2]

HEX_COLOR = re.compile(r"#[0-9a-fA-F]{3}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{8}\b")
RGB_FN = re.compile(r"\brgba?\(")
PX_VALUE = re.compile(r"(-?\d+(?:\.\d+)?)px\b")


def find_raw_style_values(text: str) -> list[str]:
    hits = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if "noqa: raw-style" in line:
            continue
        found = []
        if HEX_COLOR.search(line):
            found.append("couleur hex")
        if RGB_FN.search(line):
            found.append("rgb()/rgba()")
        for m in PX_VALUE.finditer(line):
            try:
                val = float(m.group(1))
            except ValueError:
                continue
            if val not in (0, 1):
                found.append(f"{m.group(0)}")
                break
        if found:
            hits.append(f"  ligne {lineno} ({', '.join(found)}) : {line.strip()[:100]}")
    return hits


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    path = (payload.get("tool_input", {}) or {}).get("file_path", "") or ""
    if not path or not path.endswith((".vue", ".ts", ".js")):
        sys.exit(0)

    norm = path.replace("\\", "/")
    if "/web/" not in f"/{norm}" and not norm.startswith("web/"):
        sys.exit(0)
    if norm.endswith((".spec.ts", ".test.ts", ".spec.js", ".test.js")):
        sys.exit(0)

    file_path = pathlib.Path(path)
    if not file_path.exists():
        sys.exit(0)

    web_dir = RACINE / "web"

    def local_bin(name: str) -> str | None:
        # npx via shell=False echoue sur Windows (shim .cmd, pas un .exe) ; on
        # invoke donc le binaire local directement, avec shell=True.
        cmd = web_dir / "node_modules" / ".bin" / f"{name}.cmd"
        if cmd.exists():
            return str(cmd)
        bare = web_dir / "node_modules" / ".bin" / name
        return str(bare) if bare.exists() else None

    messages = []
    for name, action in (("eslint", "--fix"), ("prettier", "--write")):
        bin_path = local_bin(name)
        if bin_path is None:
            continue  # outillage pas installe : silencieux
        try:
            result = subprocess.run(
                [bin_path, action, str(file_path)],
                capture_output=True, text=True, timeout=60, cwd=web_dir, shell=True,
            )
        except Exception:
            continue
        if result.returncode not in (0,):
            out = (result.stdout + result.stderr).strip()
            if out:
                messages.append(f"{name} : {out[:300]}")

    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        text = ""

    raw_hits = find_raw_style_values(text) if text else []
    if raw_hits:
        messages.append(
            "valeurs de style brutes detectees (CLAUDE.md : toujours un token) :\n"
            + "\n".join(raw_hits[:8])
        )

    if messages:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "⚠️ format_web (" + path + ") :\n" + "\n".join(messages),
            }
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
