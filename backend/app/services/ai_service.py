import json
import urllib.request
import urllib.error
import os

class AIService:
    def __init__(self):
        # Utilisation de l'API d'Ollama locale par défaut
        self.ollama_url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/chat")
        # qwen2.5:7b est configuré par défaut pour un raisonnement et des analyses d'une grande précision.
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
        
    def analyze_blurting(self, note_title: str, note_content: str, user_blurting: str) -> dict:
        """
        Compare la note originale (le cours modèle) avec le blurting rédigé par l'étudiant.
        Retourne une analyse sous forme de dictionnaire JSON.
        """
        # Détermination du nombre de flashcards adaptatif (plus nombreuses et exhaustives) selon la taille de la note
        word_count = len(note_content.split())
        if word_count < 150:
            max_cards_desc = "d'environ 3 à 5 cartes mémoires"
        elif word_count < 600:
            max_cards_desc = "d'environ 6 à 10 cartes mémoires"
        else:
            max_cards_desc = "d'environ 12 à 18 cartes mémoires"

        system_prompt = (
            "Tu es un tuteur d'apprentissage IA expert et bienveillant. Ton rôle est de mener une analyse comparative approfondie "
            "entre la Note Modèle (le cours original) et la Page Blanche (la restitution de mémoire écrite par l'étudiant).\n"
            "Analyse avec précision non seulement la présence des mots-clés, mais aussi la logique de raisonnement, les relations de cause à effet "
            "et les éventuelles approximations ou erreurs de compréhension.\n\n"
            "Tu dois impérativement renvoyer uniquement un objet JSON valide contenant exactement les clés suivantes :\n"
            "- \"retention_score\": un nombre entier de 0 à 100 évaluant la fidélité, l'exactitude et la complétude des concepts clés retenus.\n"
            "- \"concepts\": une liste des concepts et idées clés du cours original. Chaque objet contient :\n"
            "  * \"name\": le nom du concept.\n"
            "  * \"status\": \"mastered\" (correctement et pleinement restitué), \"missed\" (complètement oublié) ou \"incorrect\" (compris de travers/contresens/approximation).\n"
            "  * \"explanation\": une explication comparative détaillée (1 à 3 phrases) justifiant ton évaluation par rapport à ce que l'étudiant a écrit.\n"
            "- \"suggested_flashcards\": une liste [MAX_CARDS_PLACEHOLDER] basées sur les concepts oubliés ou mal compris (\"missed\" ou \"incorrect\") afin de couvrir l'intégralité des lacunes. Chaque carte contient :\n"
            "  * \"front\": une question claire, ciblée et structurée sollicitant un effort de mémoire actif.\n"
            "  * \"back\": une réponse complète, structurée et pédagogique issue fidèlement du cours original.\n"
            "- \"general_feedback\": un bilan global détaillé (un paragraphe de 3 à 5 phrases) analysant la méthode de l'étudiant, ses points forts de mémorisation, ses faiblesses à retravailler, et un plan d'action d'apprentissage.\n\n"
            "Rédige tout en français. Renvoie uniquement le JSON brut, sans introduction ni conclusion."
        ).replace("[MAX_CARDS_PLACEHOLDER]", max_cards_desc)
        
        user_message = (
            f"Note Modèle (Le cours original) :\n"
            f"Titre : {note_title}\n"
            f"Contenu :\n{note_content}\n\n"
            f"Restitution de l'étudiant (Ce qu'il a rédigé de mémoire) :\n"
            f"{user_blurting}"
        )
        
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "format": "json",
            "keep_alive": "15m",
            "options": {
                "temperature": 0.2,       # Température basse pour privilégier la rigueur logique et le respect du format JSON
                "top_p": 0.9,             # Équilibre de diversité
                "num_ctx": 4096,          # Limitation du contexte à 4096 tokens pour optimiser la mémoire et le temps d'inférence
                "num_predict": 3072       # Limite augmentée à 3072 tokens pour éviter les troncatures sur de longs rendus de flashcards
            }
        }
        
        try:
            req = urllib.request.Request(
                self.ollama_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            # Temps d'attente maximum de 60 secondes (1 minute) pour le modèle local
            with urllib.request.urlopen(req, timeout=60) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                content = res_data.get("message", {}).get("content", "")
                
                # Extraction robuste du bloc JSON par recherche d'accolades
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx+1]
                else:
                    json_str = content
                
                return json.loads(json_str)
                
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Impossible de se connecter au service d'IA local Ollama ({self.ollama_url}). "
                "Veuillez vous assurer qu'Ollama est démarré (`ollama serve`) et que le modèle est disponible."
            ) from e
        except json.JSONDecodeError as e:
            raise RuntimeError(
                "Le modèle d'IA a renvoyé une réponse invalide qui n'a pas pu être analysée comme du JSON."
            ) from e
        except Exception as e:
            raise RuntimeError(f"Une erreur est survenue lors de l'analyse IA : {str(e)}") from e
