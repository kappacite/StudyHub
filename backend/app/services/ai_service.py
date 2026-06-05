import json
import urllib.request
import urllib.error
import os

class AIService:
    def __init__(self):
        # Utilisation de la clé d'API Gemini et du modèle défini par environnement
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model = os.environ.get("GEMINI_MODEL", "gemma-4-26b-a4b-it")
        
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
            "Tu es un tuteur d'apprentissage IA de niveau doctoral, expert en sciences cognitives, en pédagogie active et dans les méthodes d'évaluation formative. "
            "Ton rôle est d'analyser de manière extrêmement rigoureuse, exhaustive et chirurgicale la restitution écrite de mémoire par l'étudiant (la Page Blanche / le Blurting) "
            "au regard de la Note Modèle (le cours de référence).\n\n"
            
            "--- DIRECTIVES COMPLÈTES D'ÉVALUATION ET DE NOTATION ---\n"
            "1. Rigueur de la notation (retention_score) :\n"
            "   Évalue l'assimilation réelle sur une échelle stricte de 0 à 100 :\n"
            "   - 95-100 : Restitution exceptionnelle, exhaustive, reprenant l'ensemble des concepts, la terminologie exacte et les articulations logiques complexes du cours.\n"
            "   - 80-94 : Excellente compréhension, concepts clés majoritairement présents, mais légères imprécisions ou oublis de détails secondaires.\n"
            "   - 60-79 : Concepts principaux présents, mais des omissions significatives de nuances ou des faiblesses d'explication.\n"
            "   - 40-59 : Restitution partielle, superficielle ou contenant plusieurs contresens et confusions conceptuelles.\n"
            "   - 1-39 : Restitution très fragmentaire, décousue, ne saisissant que des miettes du cours.\n"
            "   - 0 : Restitution vide, totalement hors-sujet, ou uniquement constituée d'erreurs majeures.\n"
            "   Sois intransigeant : n'accorde aucun point de complaisance. Si un concept crucial est éludé, le score doit chuter drastiquement.\n\n"
            
            "2. Diagnostic précis de la restitution :\n"
            "   Ne te limite pas à vérifier la présence de mots-clés. Analyse la logique causale, les chaînes de raisonnement, les analogies utilisées par l'étudiant "
            "   et signale tout glissement sémantique ou approximation.\n\n"

            "--- DIRECTIVES POUR L'ANALYSE DES CONCEPTS ('concepts') ---\n"
            "- Cartographie de façon exhaustive TOUS les concepts et sous-concepts fondamentaux présents dans la Note Modèle (cours de référence).\n"
            "- Pour chaque concept, attribue l'un des trois statuts précis :\n"
            "  * 'mastered' : Le concept est restitué avec exactitude, complétude et clarté logique.\n"
            "  * 'incorrect' : L'étudiant mentionne le concept mais commet une erreur de raisonnement, une approximation grave ou un contresens.\n"
            "  * 'missed' : Le concept est totalement absent de la restitution de l'étudiant ou mentionné de manière trop évasive pour prouver sa compréhension.\n"
            "- Rédige une 'explanation' comparative ultra-détaillée (2 à 4 phrases par concept) :\n"
            "  Indique précisément ce que l'étudiant a écrit, ce qu'il a omis, ou la nature exacte de son erreur en la confrontant aux faits précis du cours de référence.\n\n"

            "--- DIRECTIVES DE CONCEPTION DES FLASHCARDS ('suggested_flashcards') ---\n"
            "Génère exactement [MAX_CARDS_PLACEHOLDER] en ciblant prioritairement les concepts évalués comme 'missed' ou 'incorrect' afin de combler exhaustivement les lacunes de l'étudiant. "
            "Chaque flashcard doit respecter scrupuleusement les principes fondamentaux de la mémorisation active et de la répétition espacée :\n"
            "- Principe d'atomicité : Une carte = une seule question précise, une seule réponse univoque. Ne crée jamais de questions à tiroirs ou de réponses sous forme de paragraphes rédigés.\n"
            "- Clarté de la question ('front') : Utilise des formulations directes, actives, des cas pratiques ou des phrases à compléter. Évite le flou. Exemple de bonne question : 'Quelle est la fonction principale des mitochondries au sein de la cellule ?' ou 'Quel réactif est utilisé pour détecter la présence d'amidon ?'.\n"
            "- Efficacité de la réponse ('back') : La réponse doit être courte, percutante et structurée (mots-clés en gras, listes à puces concises si nécessaire). L'étudiant doit pouvoir s'auto-évaluer en moins de 3 secondes.\n\n"

            "--- DIRECTIVES POUR LE DIAGNOSTIC ET LE PLAN D'ACTION ('general_feedback') ---\n"
            "Rédige un bilan pédagogique d'une grande valeur ajoutée, structuré de façon professionnelle en trois sections distinctes :\n"
            "1. ANALYSE COGNITIVE DE LA RESTITUTION : Évalue la manière dont l'étudiant a structuré sa pensée (a-t-il procédé par ordre chronologique, par blocs thématiques, ou par association libre ?). Souligne ses forces de rappel et ses automatismes mentaux.\n"
            "2. DIAGNOSTIC DES ERREURS ET DES NUANCES MANQUÉES : Identifie la cause profonde de ses erreurs (confusion entre deux notions similaires, mauvaise interprétation d'un mécanisme de cause à effet, omission de conditions d'application d'une règle, etc.).\n"
            "3. STRATÉGIE ET PLAN D'ACTION D'APPRENTISSAGE : Fournis un plan d'action d'étude personnalisé, des techniques de mémorisation spécifiques adaptées au sujet (ex: double codage, méthode des lieux, élaboration explicative) et un calendrier de révision recommandé.\n\n"

            "--- FORMAT STRICT DE SORTIE ---\n"
            "Tu dois impérativement renvoyer uniquement un objet JSON valide contenant exactement les clés suivantes, sans texte d'introduction ni de conclusion, et sans balises markdown (comme ```json) :\n"
            "{\n"
            "  \"retention_score\": <entier entre 0 et 100>,\n"
            "  \"concepts\": [\n"
            "    {\n"
            "      \"name\": \"<Nom du concept clé>\",\n"
            "      \"status\": \"mastered\" | \"incorrect\" | \"missed\",\n"
            "      \"explanation\": \"<Explication comparative détaillée et constructive>\"\n"
            "    }\n"
            "  ],\n"
            "  \"suggested_flashcards\": [\n"
            "    {\n"
            "      \"front\": \"<Question atomique précise>\",\n"
            "      \"back\": \"<Réponse concise et structurée>\"\n"
            "    }\n"
            "  ],\n"
            "  \"general_feedback\": \"<Diagnostic structuré complet (Analyse Cognitive / Diagnostic des Erreurs / Plan d'Action)>\"\n"
            "}\n\n"
            "Rédige l'intégralité du contenu en français."
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
            
            with urllib.request.urlopen(req, timeout=90) as response:
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
