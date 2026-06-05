import json
import urllib.request
import urllib.error
import os

class AIService:
    def __init__(self):
        # Utilisation de la clé d'API Gemini et du modèle défini par environnement
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model = os.environ.get("GEMINI_MODEL", "gemma-4-31b")
        
    def analyze_blurting(self, note_title: str, note_content: str, user_blurting: str) -> dict:
        """
        Compare la note originale (le cours modèle) avec le blurting rédigé par l'étudiant via l'API Gemini.
        Retourne une analyse sous forme de dictionnaire JSON.
        """
        if not self.api_key:
            raise RuntimeError(
                "La clé d'API Gemini n'est pas configurée. "
                "Veuillez définir la variable d'environnement GEMINI_API_KEY dans votre fichier .env."
            )
            
        # Détermination du nombre de flashcards adaptatif selon la taille de la note
        word_count = len(note_content.split())
        if word_count < 150:
            max_cards_desc = "d'environ 3 à 5 cartes mémoires"
        elif word_count < 600:
            max_cards_desc = "d'environ 6 à 10 cartes mémoires"
        else:
            max_cards_desc = "d'environ 12 à 18 cartes mémoires"

        system_prompt = (
            "Tu es un tuteur d'apprentissage IA de niveau universitaire, hautement qualifié et pédagogue. "
            "Ton rôle est d'effectuer une analyse comparative rigoureuse, objective et constructive "
            "entre la Note Modèle (le cours de référence) et la Page Blanche (la restitution écrite de mémoire par l'étudiant).\n\n"
            
            "Directives pour l'évaluation et la notation :\n"
            "1. Sois exigeant sur le 'retention_score' (note de 0 à 100) : il doit refléter fidèlement le taux d'assimilation. "
            "N'attribue pas de points de complaisance. Un score supérieur à 90 requiert une restitution quasi-parfaite de la logique et des faits clés. "
            "Si la restitution est vide, hors-sujet ou incohérente, le score doit être de 0.\n"
            "2. Analyse minutieusement la précision scientifique/technique, la logique de cause à effet, les mots-clés essentiels "
            "et décèle les contresens, approximations ou confusions.\n\n"

            "Directives pour l'analyse des concepts ('concepts') :\n"
            "- Identifie tous les piliers fondamentaux de la Note Modèle.\n"
            "- Pour chaque concept, qualifie son statut : \n"
            "  * 'mastered' : Restitué de façon complète, exacte et sans ambiguïté.\n"
            "  * 'incorrect' : Restitué avec des contresens, des approximations critiques ou confondu avec un autre concept.\n"
            "  * 'missed' : Complètement absent ou trop superficiel pour être validé.\n"
            "- Rédige une 'explanation' comparative précise (1 à 3 phrases) détaillant exactement ce qui a été bien restitué "
            "ou ce qui fait défaut par rapport au cours de référence.\n\n"

            "Directives pour les fiches de révision suggérées ('suggested_flashcards') :\n"
            "- Génère [MAX_CARDS_PLACEHOLDER] focalisées sur les concepts marqués comme 'missed' ou 'incorrect'.\n"
            "- Respecte le principe de l'atomicité : une question doit porter sur une seule information clé, claire et ciblée. "
            "Évite les questions trop larges ou vagues.\n"
            "- La réponse ('back') doit être concise, percutante, exacte et immédiatement mémorisable, issue directement du cours.\n\n"

            "Directives pour le bilan global ('general_feedback') :\n"
            "- Rédige un diagnostic pédagogique structuré en 3 parties :\n"
            "  1. Analyse de la restitution (forces et axes d'amélioration de la mémorisation).\n"
            "  2. Identification des biais cognitifs ou erreurs logiques détectées.\n"
            "  3. Un plan d'action d'apprentissage précis (ex. conseils sur les associations d'idées, la structure des révisions).\n\n"

            "Format de sortie :\n"
            "Tu dois impérativement renvoyer uniquement un objet JSON valide contenant exactement les clés :\n"
            "- \"retention_score\": entier de 0 à 100\n"
            "- \"concepts\": liste d'objets avec \"name\" (str), \"status\" (str : 'mastered'|'incorrect'|'missed'), \"explanation\" (str)\n"
            "- \"suggested_flashcards\": liste d'objets avec \"front\" (str), \"back\" (str)\n"
            "- \"general_feedback\": chaîne de caractères contenant le diagnostic structuré.\n\n"
            "Rédige tout en français. Renvoie uniquement le JSON brut, sans introduction, sans conclusion, et sans balises markdown."
        ).replace("[MAX_CARDS_PLACEHOLDER]", max_cards_desc)
        
        user_message = (
            f"Note Modèle (Le cours original) :\n"
            f"Titre : {note_title}\n"
            f"Contenu :\n{note_content}\n\n"
            f"Restitution de l'étudiant (Ce qu'il a rédigé de mémoire) :\n"
            f"{user_blurting}"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": user_message}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2
            }
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                
                candidates = res_data.get("candidates", [])
                if not candidates:
                    raise RuntimeError("Aucun candidat renvoyé par l'API Gemini.")
                    
                candidate = candidates[0]
                content_obj = candidate.get("content", {})
                parts = content_obj.get("parts", [])
                if not parts:
                    raise RuntimeError("Aucune partie de contenu renvoyée par l'API Gemini.")
                    
                content = parts[0].get("text", "")
                
                # Extraction robuste du bloc JSON par recherche d'accolades
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx+1]
                else:
                    json_str = content
                
                return json.loads(json_str)
                
        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                pass
            raise RuntimeError(
                f"Erreur HTTP lors de l'appel à l'API Gemini ({e.code}) : {e.reason}. Détails : {error_body}"
            ) from e
        except urllib.error.URLError as e:
            raise RuntimeError(
                "Impossible de se connecter à l'API Gemini. "
                "Veuillez vérifier votre connexion internet et les paramètres réseau."
            ) from e
        except json.JSONDecodeError as e:
            raise RuntimeError(
                "Le modèle d'IA Gemini a renvoyé une réponse invalide qui n'a pas pu être analysée comme du JSON."
            ) from e
        except Exception as e:
            raise RuntimeError(f"Une erreur est survenue lors de l'analyse IA avec Gemini : {str(e)}") from e
