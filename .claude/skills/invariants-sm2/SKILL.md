---
name: invariants-sm2
description: Spécification formelle de l'algorithme SM-2 (SuperMemo-2) tel qu'implémenté dans StudyHub — facteur de facilité, plancher, progression des intervalles, échec, jour d'étude/streak. À charger avant de toucher à la planification de révision.
---

# invariants-sm2

Référence unique : `backend/app/services/spaced_repetition.py` (`calculate_sm2`). Ce skill
documente le comportement **réel** — toute modification touchant à la planification doit faire
passer les tests de `backend/tests/test_spaced_repetition.py` **à l'identique** ; ce sont les
fixtures de non-régression qui font foi, pas ce document s'ils divergent un jour (dans ce cas
c'est ce fichier qui est faux et doit être corrigé).

## Signature

```python
calculate_sm2(score: int, ease_factor: float, interval: int, repetitions: int, tuning: float = 1.0)
    -> tuple[ease_factor: float, new_interval: int, new_repetitions: int, next_review: datetime]
```

## Invariants

1. **Facteur de facilité (ease factor)** :
   `EF' = EF + (0.1 - (5 - score) * (0.08 + (5 - score) * 0.02))`, puis **plancher absolu à
   1.30** (`max(1.3, ease_factor)`) — ne descend jamais en dessous, quel que soit le score.
2. **Révision réussie (`score >= 3`)** :
   - `repetitions == 0` → `new_interval = 1`
   - `repetitions == 1` → `new_interval = 6`
   - `repetitions >= 2` → `new_interval = round(interval * new_ease_factor)`
   - `new_repetitions = repetitions + 1`
3. **Révision ratée (`score < 3`, soit 0/1/2)** : reset complet —
   `new_repetitions = 0`, `new_interval = 1`, **quel que soit l'état précédent** (même après
   des dizaines de répétitions réussies).
4. **Fine-tuning (`tuning`, paramètre D4)** : multiplicateur appliqué **après** le calcul
   normal de l'intervalle, seulement si `tuning > 0 and tuning != 1.0` ; plancher à 1 jour
   (`max(1, round(new_interval * tuning))`). Sans effet sur l'ease factor. Permet de réviser
   une carte plus souvent (`< 1.0`) ou plus rarement (`> 1.0`) qu'un SM-2 pur.
5. **Prochaine révision** : `next_review = datetime.utcnow() + timedelta(days=new_interval)`.

## Jour d'étude et streak — fuseau horaire

`backend/app/services/stats_service.py::_calculate_streak` définit le "jour d'étude" en
**UTC**, pas en heure locale de l'utilisateur : `datetime.utcnow().date()`. Le streak continue
si une session existe pour `aujourd'hui` (UTC) ou `hier` (UTC) ; sinon il retombe à 0. Compter
implique de remonter jour par jour tant qu'une session existe.

**Conséquence à connaître** : un utilisateur qui étudie juste après minuit heure locale mais
avant minuit UTC (ou l'inverse) peut voir son streak se comporter différemment de son intuition
locale. C'est un comportement actuel, pas forcément voulu — un constat pour `docs/audit/`
phase 2, pas un bug à corriger de sa propre initiative.

## Ce qui n'est PAS couvert par ce module

`calculate_sm2` est une fonction pure sans effet de bord (pas d'accès DB). L'orchestration
(charger la carte, appeler `calculate_sm2`, persister le résultat) vit dans
`flashcard_service.py`/`revision_service.py` — ce sont ces services qui appliquent
l'isolation `user_id`, pas cette fonction.
