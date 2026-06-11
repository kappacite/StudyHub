import zipfile
import io
import sqlite3
import tempfile
import os
import json
from typing import List, Dict, Any, Tuple

def parse_apkg(file_bytes: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Parse un fichier Anki .apkg et extrait les decks et leurs cartes.
    
    Retourne:
        - Une liste de dictionnaires deck: { name: str, cards: List[{ front, back, tags }] }
        - Une liste d'avertissements (warnings)
    """
    try:
        z = zipfile.ZipFile(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError("Le fichier n'est pas une archive ZIP (apkg) valide.") from e

    # Recherche du fichier SQLite contenant la collection
    sqlite_filename = None
    for name in z.namelist():
        if name.startswith("collection.anki2"):
            sqlite_filename = name
            break
            
    if not sqlite_filename:
        raise ValueError("La collection Anki (collection.anki2) est introuvable dans l'archive.")

    try:
        db_bytes = z.read(sqlite_filename)
    except Exception as e:
        raise ValueError("Impossible de lire le fichier collection.anki2 dans l'archive.") from e
    
    # Écriture dans un fichier temporaire pour pouvoir l'ouvrir avec sqlite3
    fd, temp_db_path = tempfile.mkstemp(suffix=".anki2")
    conn = None
    try:
        with os.fdopen(fd, 'wb') as tmp:
            tmp.write(db_bytes)
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Lecture de la configuration de la collection pour obtenir les noms de decks
        try:
            cursor.execute("SELECT decks FROM col")
            col_row = cursor.fetchone()
        except sqlite3.OperationalError as e:
            raise ValueError("Structure de base de données Anki invalide ou corrompue.") from e
            
        if not col_row:
            raise ValueError("Configuration de la collection Anki vide.")
            
        try:
            decks_info = json.loads(col_row[0])
        except Exception as e:
            raise ValueError("Configuration des decks Anki corrompue (JSON invalide).") from e
        
        # Récupération des notes et cartes associées
        try:
            cursor.execute("""
                SELECT c.did, n.id, n.flds, n.tags 
                FROM cards c 
                JOIN notes n ON c.nid = n.id
            """)
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            raise ValueError("Structure de table notes/cards Anki invalide ou corrompue.") from e
        
        deck_cards: Dict[int, List[Dict[str, Any]]] = {}
        warnings: List[str] = []
        
        seen_notes = set()
        has_html = False
        has_multified = False
        
        for did, nid, flds, tags in rows:
            # Évite d'importer plusieurs fois la même note si elle génère plusieurs templates de cartes
            if nid in seen_notes:
                continue
            seen_notes.add(nid)
            
            # Anki sépare les champs de note par le caractère \x1f
            fields = flds.split("\x1f")
            
            if len(fields) == 0:
                front = ""
                back = ""
            elif len(fields) == 1:
                front = fields[0]
                back = ""
            else:
                front = fields[0]
                back = fields[1]
                if len(fields) > 2:
                    has_multified = True
            
            # Détection d'HTML
            if ("<" in front and ">" in front) or ("<" in back and ">" in back):
                has_html = True
                
            # Les tags dans Anki sont des chaînes séparées par des espaces (ex: "tag1 tag2")
            parsed_tags = [t.strip() for t in tags.strip().split(" ") if t.strip()]
            
            card_data = {
                "front": front.strip(),
                "back": back.strip(),
                "tags": parsed_tags
            }
            
            if did not in deck_cards:
                deck_cards[did] = []
            deck_cards[did].append(card_data)
            
        if has_multified:
            warnings.append("Certaines cartes contiennent plus de 2 champs. Seuls les deux premiers champs ont été importés comme recto / verso.")
            
        if has_html:
            warnings.append("Des cartes contenant du code HTML ont été détectées. Le formatage HTML a été importé tel quel.")
            
        # Construction des decks finaux
        decks_list = []
        for did, cards in deck_cards.items():
            deck_meta = decks_info.get(str(did), {})
            deck_name = deck_meta.get("name", f"Deck {did}")
            
            # Anki stocke les sous-decks séparés par "::", on peut conserver ce nom
            decks_list.append({
                "name": deck_name,
                "cards": cards
            })
            
        return decks_list, warnings
        
    finally:
        if conn:
            conn.close()
        try:
            os.remove(temp_db_path)
        except Exception:
            pass
