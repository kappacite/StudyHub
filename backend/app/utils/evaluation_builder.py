"""Conversion des balises de note (placeholders) en items d'évaluation.

Les balises issues de `extract_placeholders_from_text` portent déjà leur réponse,
donc ces items sont corrigés automatiquement sans appel IA :
- qcm   -> item 'qcm' (options + bonne réponse re-parsées depuis le raw_tag)
- vf    -> item 'vf'  (assertion + booléen + justification)
- trou  -> item 'trou' (phrase avec [...] + réponse)
- def / ordre / assoc -> item 'open' (question + réponse-modèle auto-évaluée)
"""
import re
from typing import Any, Dict, Optional, Tuple

_QCM_RE = re.compile(r"\{\{qcm::(.*?)::(.*?)\}\}")
_VF_RE = re.compile(r"\{\{vf::(.*?)::(.*?)::(.*?)\}\}")

_OPTION_IDS = ["a", "b", "c", "d", "e", "f", "g", "h"]


def placeholder_to_eval_item(placeholder: Dict[str, Any]) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Retourne (type, payload) pour un EvaluationItem, ou None si non convertible."""
    p_type = placeholder.get("type")
    raw_tag = placeholder.get("raw_tag", "")
    front = (placeholder.get("front") or "").strip()
    back = (placeholder.get("back") or "").strip()

    if p_type == "qcm":
        m = _QCM_RE.search(raw_tag)
        if not m:
            return None
        question = m.group(1).strip()
        options = []
        for idx, raw_opt in enumerate(m.group(2).split("|")):
            opt = raw_opt.strip()
            correct = False
            star = re.fullmatch(r"\*(.*)\*", opt)
            if star:
                opt = star.group(1).strip()
                correct = True
            options.append({"id": _OPTION_IDS[idx] if idx < len(_OPTION_IDS) else str(idx), "text": opt, "correct": correct})
        return "qcm", {"question": question, "options": options}

    if p_type == "vf":
        m = _VF_RE.search(raw_tag)
        if not m:
            return None
        assertion = m.group(1).strip()
        correct = m.group(2).strip().lower().startswith("v")
        justification = m.group(3).strip()
        return "vf", {"assertion": assertion, "correct": correct, "justification": justification}

    if p_type == "trou":
        # front = "Texte à trous :\n<phrase avec [...]>"
        text = front.split("\n", 1)[-1].strip() if "\n" in front else front
        return "trou", {"text_with_blank": text, "answer": back}

    if p_type in ("def", "ordre", "assoc"):
        return "open", {"question": front, "model_answer": back, "key_points": []}

    return None
