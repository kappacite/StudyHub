import re

# Balises dont le contenu doit être supprimé intégralement (exécutables / inertes dangereux).
_DANGEROUS_BLOCK_RE = re.compile(
    r"<(script|style|iframe|object|embed|noscript|template|svg|math)\b[\s\S]*?</\1\s*>",
    flags=re.IGNORECASE,
)
# Mêmes balises sous forme non fermée / auto-fermante + balises d'en-tête sensibles.
_DANGEROUS_TAG_RE = re.compile(
    r"<\/?(script|style|iframe|object|embed|noscript|template|svg|math|link|meta|base)\b[^>]*>",
    flags=re.IGNORECASE,
)
# Gestionnaires d'événements inline : on*="…" / on*='…' / on*=valeur.
_EVENT_HANDLER_RE = re.compile(
    r"""\s+on\w+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""",
    flags=re.IGNORECASE,
)
# URIs exécutables dans href/src (javascript:, data:, vbscript:).
_DANGEROUS_URI_RE = re.compile(
    r"""(href|src|xlink:href)\s*=\s*(["']?)\s*(?:javascript|data|vbscript):[^"'\s>]*\2""",
    flags=re.IGNORECASE,
)


def sanitize_html(content: str) -> str:
    """Assainit le contenu d'une note **sans corrompre le Markdown**.

    Les notes StudyHub sont stockées en Markdown brut (l'éditeur est un textarea
    Markdown) et rendues côté client via `marked` puis `DOMPurify` (couche de
    défense XSS principale, au moment du rendu). Faire passer ce Markdown dans un
    sanitizer HTML classique (bleach) échappait les caractères structurels du
    Markdown (`>` des citations, `<`, `&`) en entités HTML, cassant l'affichage —
    notamment lors d'une copie où le contenu était ré-échappé.

    Ici on se contente donc d'une défense en profondeur ciblée : on retire les
    constructions réellement exécutables (script/iframe/handlers `on*`, URIs
    `javascript:`…) tout en laissant la ponctuation Markdown intacte.
    """
    if not content:
        return ""

    cleaned = _DANGEROUS_BLOCK_RE.sub("", content)
    cleaned = _DANGEROUS_TAG_RE.sub("", cleaned)
    cleaned = _EVENT_HANDLER_RE.sub("", cleaned)
    cleaned = _DANGEROUS_URI_RE.sub(r"\1=\2#\2", cleaned)
    return cleaned
