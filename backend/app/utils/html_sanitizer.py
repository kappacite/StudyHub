import bleach
import re
from bleach.css_sanitizer import CSSSanitizer

def sanitize_html(html_content: str) -> str:
    """
    Assainit le code HTML provenant de l'éditeur riche (Tiptap) pour prévenir les failles XSS
    tout en préservant le formatage légitime.
    """
    if not html_content:
        return ""
        
    # Nettoyer complètement les balises script et iframe (et leur contenu) pour éviter qu'elles ne soient conservées sous forme de texte brut
    content_clean = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html_content, flags=re.IGNORECASE)
    content_clean = re.sub(r'<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>', '', content_clean, flags=re.IGNORECASE)
        
    allowed_tags = [
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul',
        'p', 'span', 'u', 's', 'pre', 'br', 'hr',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'img'
    ]
    
    allowed_attributes = {
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        '*': ['class', 'style']
    }
    
    allowed_styles = [
        'color', 'background-color', 'text-align', 'font-size', 'font-family',
        'font-weight', 'font-style', 'text-decoration'
    ]
    
    css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_styles)
    
    return bleach.clean(
        content_clean,
        tags=allowed_tags,
        attributes=allowed_attributes,
        css_sanitizer=css_sanitizer,
        strip=True
    )
