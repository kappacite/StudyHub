import re
import hashlib
from typing import List, Dict, Any

def generate_placeholder_hash(note_id: int, index: int, raw_tag: str) -> str:
    hash_input = f"{note_id}:{index}:{raw_tag}"
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

def extract_placeholders_from_text(content: str, note_id: int) -> List[Dict[str, Any]]:
    placeholders = []
    lines = content.split('\n')
    
    # 1. Trou: {{trou::mot caché}}
    trou_re = re.compile(r"\{\{trou::(.*?)\}\}")
    # 2. QCM: {{qcm::Question ?::Option1|*Bonne Option*|Option3}}
    qcm_re = re.compile(r"\{\{qcm::(.*?)::(.*?)\}\}")
    # 3. Ordre: {{ordre::Titre::Étape 1 > Étape 2 > Étape 3}}
    ordre_re = re.compile(r"\{\{ordre::(.*?)::(.*?)\}\}")
    # 4. Assoc: {{assoc::Titre::A=1 | B=2 | C=3}}
    assoc_re = re.compile(r"\{\{assoc::(.*?)::(.*?)\}\}")
    # 5. VF: {{vf::Affirmation::Vrai/Faux::Justification}}
    vf_re = re.compile(r"\{\{vf::(.*?)::(.*?)::(.*?)\}\}")

    placeholder_idx = 0

    for line_num, line in enumerate(lines):
        # On va chercher tous les placeholders dans la ligne de manière ordonnée
        
        # --- Trou ---
        for match in trou_re.finditer(line):
            raw_tag = match.group(0)
            hidden_word = match.group(1)
            
            # Contexte: Remplacer le tag par [...] dans la ligne courante
            front_text = line.replace(raw_tag, "[...]")
            # Nettoyer les autres tags pour qu'ils soient lisibles
            front_text = re.sub(r"\{\{trou::(.*?)\}\}", r"\1", front_text)
            front_text = re.sub(r"\{\{qcm::.*?::(.*?)\}\}", r"\1", front_text)
            front_text = re.sub(r"\{\{ordre::.*?::(.*?)\}\}", r"\1", front_text)
            front_text = re.sub(r"\{\{assoc::.*?::(.*?)\}\}", r"\1", front_text)
            front_text = re.sub(r"\{\{vf::(.*?)::.*?::.*?\}\}", r"\1", front_text)
            
            placeholders.append({
                "index": placeholder_idx,
                "raw_tag": raw_tag,
                "type": "trou",
                "front": f"Texte à trous :\n{front_text.strip()}",
                "back": hidden_word.strip(),
                "hash": generate_placeholder_hash(note_id, placeholder_idx, raw_tag)
            })
            placeholder_idx += 1

        # --- QCM ---
        for match in qcm_re.finditer(line):
            raw_tag = match.group(0)
            question = match.group(1)
            options_str = match.group(2)
            
            # Trouver l'option correcte entourée d'étoiles
            correct_match = re.search(r"\*(.*?)\*", options_str)
            correct_answer = correct_match.group(1) if correct_match else "Option correcte non spécifiée"
            
            placeholders.append({
                "index": placeholder_idx,
                "raw_tag": raw_tag,
                "type": "qcm",
                "front": f"QCM : {question.strip()}",
                "back": correct_answer.strip(),
                "hash": generate_placeholder_hash(note_id, placeholder_idx, raw_tag)
            })
            placeholder_idx += 1

        # --- Ordre ---
        for match in ordre_re.finditer(line):
            raw_tag = match.group(0)
            title = match.group(1)
            sequence = match.group(2)
            
            placeholders.append({
                "index": placeholder_idx,
                "raw_tag": raw_tag,
                "type": "ordre",
                "front": f"Mettre dans l'ordre : {title.strip()}",
                "back": sequence.strip(),
                "hash": generate_placeholder_hash(note_id, placeholder_idx, raw_tag)
            })
            placeholder_idx += 1

        # --- Assoc ---
        for match in assoc_re.finditer(line):
            raw_tag = match.group(0)
            title = match.group(1)
            pairs = match.group(2)
            
            placeholders.append({
                "index": placeholder_idx,
                "raw_tag": raw_tag,
                "type": "assoc",
                "front": f"Associer les éléments : {title.strip()}",
                "back": pairs.strip(),
                "hash": generate_placeholder_hash(note_id, placeholder_idx, raw_tag)
            })
            placeholder_idx += 1

        # --- VF ---
        for match in vf_re.finditer(line):
            raw_tag = match.group(0)
            assertion = match.group(1)
            response = match.group(2)
            justification = match.group(3)
            
            placeholders.append({
                "index": placeholder_idx,
                "raw_tag": raw_tag,
                "type": "vf",
                "front": f"Vrai ou Faux :\n{assertion.strip()}",
                "back": f"{response.strip()} - Justification : {justification.strip()}",
                "hash": generate_placeholder_hash(note_id, placeholder_idx, raw_tag)
            })
            placeholder_idx += 1

    return placeholders
