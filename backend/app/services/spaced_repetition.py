from datetime import datetime, timedelta
from typing import Tuple

def calculate_sm2(
    score: int, 
    ease_factor: float, 
    interval: int, 
    repetitions: int
) -> Tuple[float, int, int, datetime]:
    """
    Implémentation de l'algorithme SuperMemo-2 (SM-2) pour la répétition espacée.
    
    Retourne un tuple : (nouveau_ease_factor, nouvel_interval, nouvelles_repetitions, date_prochaine_revision)
    """
    # 1. Calcul du nouveau facteur de facilité (ease factor)
    # Formule : EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    ease_factor = ease_factor + (0.1 - (5 - score) * (0.08 + (5 - score) * 0.02))
    ease_factor = max(1.3, ease_factor)  # Le facteur ne doit jamais descendre en dessous de 1.3
    
    # 2. Calcul des répétitions et de l'intervalle (en jours)
    if score >= 3:
        # Révision réussie
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = int(round(interval * ease_factor))
            
        new_repetitions = repetitions + 1
    else:
        # Révision ratée (score 0, 1, 2)
        new_repetitions = 0
        new_interval = 1
        
    # Calcul de la date de prochaine révision
    next_review = datetime.utcnow() + timedelta(days=new_interval)
    
    return ease_factor, new_interval, new_repetitions, next_review
