# Refonte UI structurelle StudyHub — Plan & suivi (S0 → S7)

> Document de **suivi exécutable** : permet de reprendre l'implémentation à tout moment.
> Direction visuelle **« White/Pink × Material épuré »** (primaire Pink 400 `#F06292`, light+dark) ;
> tokens/primitives dans `docs/design-system.md`. Plan complet : refonte DA + structure 5 sections.

## Avancement

Légende : ✅ fait · 🔄 en cours · ⏳ à faire

| Lot | Sous-étape | Statut | Branche |
|---|---|---|---|
| **Lot 0** | Tokens + motion + primitives `ui/base/` + `docs/design-system.md` | ✅ | `feature/ui-refactor-foundations` |
| **Lot 1** | Restyle shell `AppLayout`, `Dashboard`, Auth (`Login`/`Register`) | ✅ | `feature/ui-refactor-foundations` |
| **Lot T** | Re-theming white/pink + Material : tokens (danger→rouge), élévation, primitives `ui/base/`+`ui/*` | ✅ | `feature/ui-refactor-s0` |
| **S0.1** | Primitives `PageContainer/PageHeader/Tabs/ListRow/SplitView` + tests | ✅ | `feature/ui-refactor-s0` |
| **S0.2** | `views/Classes/ClassesLanding.vue` (coquille à onglets) | ✅ | `feature/ui-refactor-s0` |
| **S0.3** | Routing : 5 sections canoniques + redirects (partiels, voir note) | ✅ | `feature/ui-refactor-s0` |
| **S0.4** | Nav `AppLayout` : 5 sections + actif par préfixe | ✅ | `feature/ui-refactor-s0` |
| **S0.5** | Redirects auth (`/dashboard`→`/accueil`) + anti-stranding | ✅ | `feature/ui-refactor-s0` |
| **S0** | Vérif build/tests (✅ build + 66 tests) | ✅ | `feature/ui-refactor-s0` |

> **Note S0.3 — redirects séquencés** : seuls les redirects dont la cible fonctionne déjà sont
> actifs (`/dashboard`→`/accueil`, `/binders/:id?`→`/bibliotheque/:id?`, `/reviews`→`/reviser`,
> `/groups`+`/classes/teacher|student`→`/classes?tab=…`). `/focus` (anti-stranding S1), `/decks`
> (S3), `/notes`+`/pdfs`+`/diagrams` (S2) restent des **routes réelles** : les rediriger
> maintenant casserait des `router.push` internes (SearchModal `/decks?id=` & `/diagrams?id=`,
> liens Dashboard/Binders) tant que Bibliothèque/Réviser n'agrègent pas leur contenu.
| **S1** | Accueil (fusion Dashboard + Focus, action-first) — `Home/Accueil.vue`, `/focus`→`/accueil` | ✅ | `feature/ui-refactor-s0` |
| **S2** | Bibliothèque — `Binders.vue` refondu en `SplitView` (arbre + contenu typé, tabs `?type=`) | 🔄 | `feature/ui-refactor-s0` |
| **S3** | Réviser — `PageHeader`+sélecteurs tokenisés, bandeau « À réviser maintenant » (focus) + CTA « Tout réviser », entrée Examen | 🔄 | `feature/ui-refactor-s3` |
| **S4** | Classes — `StudentClassView` + `GroupsList` migrés (tokens, sous-en-tête) ; gros enfants restants | 🔄 | `feature/ui-refactor-s4` |
| **S5** | Planning — `PlanningPage` (PageHeader + toggle/nav) + `Week/MonthCalendar` tokenisés (charge→success/warning/danger) | ✅ | `feature/ui-refactor-s5` |
| **S6** | Communauté/Public — `PublicLayout`+`Home`+`Explore`+`PackagePreview`+`PublicNote` migrés | ✅ | `feature/ui-refactor-s6/s7` |
| **S7** | Finition — `PackagePreview`/`PublicNote` faits ; `prefers-reduced-motion` déjà OK ; reste composants lourds + audit visuel | 🔄 | `feature/ui-refactor-s7` |

**Reprise rapide** : `git checkout feature/ui-refactor-s0` → continuer à la 1re ligne 🔄/⏳.
Mettre à jour ce tableau à chaque sous-étape terminée.

> **État S2 (🔄)** : le **cœur est fait** — `Binders.vue` (route `bibliotheque/:id?`) est
> refondu en `SplitView` (arbre `#left` + contenu typé `#right`), `PageHeader` (fil d'Ariane),
> `Tabs` par type (`?type=`), `ListRow` + tokens `cat-*`, et **toutes** les features préservées
> (owner vs lecture-seule, clone, attache/détache, partage communauté + classe, stats).
> **Feuilles ré-agencées** : `Notes.vue` ✅ (PageHeader + BaseCard + tokens, accent `cat-note`),
> `PDFs.vue` ✅ (liste + lecteur + modale d'édition, accent `cat-pdf`), `Diagrams.vue` 🔄 (tête
> `PageHeader` + barre de filtres tokenisées ; **corps de l'éditeur visuel laissé tel quel** —
> couleurs fonctionnelles stockées en data + canevas SVG, à reprendre en passe soignée S7).
> **Reste** : `NoteEdit.vue` (mode **zen** ~68ch — mode spécial préservé, migration prudente
> reportée à S7) et le corps éditeur de `Diagrams.vue`. Lots T, S0, S1 et S2(cœur) **commités**
> sur `feature/ui-refactor-s0` (poussés).

---

## 0. Règles valables pour TOUS les lots

**But** : passer de 12 entrées de menu qui se recoupent à **5 sections par intention** —
*Accueil · Bibliothèque · Réviser · Planning · Classes* + lien *Communauté* — et ré-agencer
toutes les pages. Direction « Soft & Friendly », animations subtiles (~200 ms).

**Contraintes absolues** :
- **Aucun changement backend.** Stores Pinia, services API (`web/src/services/*`), auth : intacts.
- **Aucune perte de fonctionnalité** : on réorganise/redirige, on ne supprime jamais une feature.
- **Routes feuilles préservées** (édition, runners, stats, examen) — beaucoup de `router.push()`
  internes en dépendent. On ne change que les routes de **liste** (→ sections + redirects).
- **Modes spéciaux préservés** : zen (`NoteEdit`), immersif (`ExamSession`, `meta.immersive`),
  persistance thème `localStorage 'sh_theme'`.
- **Pas de rôle global** : `stores/auth.ts` n'a pas de `my_role`. « Prof » = administre une classe
  (`my_role` ∈ {`owner`,`admin`} sur `ClassInfo` via `classService.getMyClasses()`), sinon élève.
  ⇒ **pas de garde de rôle dans le router** ; Classes = une entrée, branchement interne.

**Conventions (chaque lot)** :
- Branche `feature/ui-refactor-sX`. Conventional Commits, un commit par sous-étape.
- Vérif : `cd web && npm run build` (vue-tsc strict + vite) et `npm run test:run` verts ;
  visuel 375/1440 px clair+sombre ; non-régression des redirections ; zen + immersif intacts.
- MAJ `docs/design-system.md` (primitives) + journal de dév + **ce tracker**.
- Pas de PR ni de push sans demande explicite. Pas de logique métier dans `ui/base/`.
- Tailwind strict : tokens sémantiques (`bg-surface`, `text-ink`, `border-line`, `bg-primary-soft`…),
  jamais de couleurs brutes. TS strict (`noUnusedLocals` → pas d'import mort).

**Faits réutilisables (confirmés)** :
- `Binders.vue` agrège déjà par dossier : sous-dossiers + notes + decks + sets + diagrammes + PDFs.
- `Reviews.vue` est déjà un hub à onglets (Classiques SM-2/QCM/VF/Association/Définition/Ordre + IA).
- `stores/focus.ts` : `items/forecast/retention`, compteurs `totalDue/lateCount/…`, file unifiée
  (`startUnifiedReview`, `getActiveItem`, `nextQueueItem`). Service `focusService`.
- `classService.getMyClasses()` → `ClassInfo[]` avec `my_role` (`owner|admin|member|follower`).

---

## Lot S0 — Socle structurel (primitives + routing + nav)

**S0.1 — Primitives `ui/base/`** (sans logique/API ; tokens ; export `index.ts` ; tests `web/tests/ui/`) :
- `PageContainer` (`size` default/narrow/wide → `max-w-6xl/3xl/7xl`, `mx-auto space-y-6` ; pas de
  padding horizontal car `AppLayout > main` applique déjà `p-6`).
- `PageHeader` (`title`, `subtitle?`, `breadcrumbs?` ; slots `#actions`, `#tabs`).
- `Tabs` (segmented control présentationnel ; `modelValue`+`tabs[{key,label,icon?,badge?}]`).
- `ListRow` (`as` div/button/router-link, `title?`/`subtitle?`/`interactive?` ; slots leading/trailing).
- `SplitView` (slots `#left`/`#right` ; empilé `<lg`, flex `lg:` `left lg:w-72`).

**S0.2 — `views/Classes/ClassesLanding.vue`** : `PageContainer`+`PageHeader`+`Tabs`
(Enseignant/Élève/Groupes) piloté par `?tab=` ; défaut selon `my_role∈{owner,admin}` ; onglet
Enseignant masqué si aucune classe administrée ; monte `TeacherDashboard`/`StudentClassView`/`GroupsList`.

**S0.3 — `router/index.ts`** : routes canoniques `accueil`→Dashboard, `bibliotheque/:id?`→Binders,
`reviser`→Reviews, `classes`→ClassesLanding (`planning` inchangé). Redirects des anciennes routes
liste (`/dashboard`,`/focus`→`/accueil` ; `/binders/:id?`→`/bibliotheque/:id?` ; `/notes`,`/pdfs`,
`/diagrams`→`/bibliotheque?type=…` ; `/reviews`,`/decks`→`/reviser` ; `/groups`,`/classes/teacher`,
`/classes/student`→`/classes?tab=…`). Routes feuilles inchangées. Catch-all + `guestOnly`→`/accueil`.

**S0.4 — `AppLayout.vue`** : `navItems` 5 sections + Communauté (Home/FolderClosed/Brain/Calendar/
GraduationCap/Compass) ; actif **par préfixe** (`item.match[]` + `startsWith`) ; ne pas toucher
zen/immersive/`sh_theme`/`currentRouteName`.

**S0.5 — Auth & anti-stranding** : `Login`/`Register`/`PublicLayout` `push('/dashboard')`→`'/accueil'` ;
liens temporaires « Voir les priorités »→`/focus` (Dashboard) et « Examen blanc »→`/exam/setup` (Reviews).

**Vérif S0** : build+tests verts ; chaque redirect ; `/notes/123`→NoteEdit, `/decks/5/study`→runner,
`/groups/7`→GroupDetail ; zen+immersif OK ; nav 375/1440 clair/sombre.

---

## Lot S1 — Accueil (fusion Dashboard + Focus, action-first)

`views/Home/Accueil.vue` (route `accueil`). `PageContainer`+`PageHeader`. **Hero** salutation+série+
CTA « Continuer à réviser » (`focus.startUnifiedReview()` → route vers `focus.getActiveItem()`).
**Gauche** file `focus.items` en `ListRow`. **Droite** « Aujourd'hui » (compteurs + mini-calendrier
échéances). **Bas** Progression (`StatCard` + heatmap condensée, widgets `/stats/*`). Retirer
anti-stranding S0. États loading/empty/error.

## Lot S2 — Bibliothèque (SplitView arbre + contenu typé)

Refondre `Binders.vue` (route `bibliotheque/:id?`) en `SplitView` : **#left** arbre classeurs
(`parent_id`, +Dossier, mobile→sélecteur) ; **#right** `PageHeader` (fil d'Ariane=chemin) + `Tabs`
type (Tout/Notes/PDF/Diagrammes/Ensembles/Decks, `?type=`) ; contenu en `ListRow` + icône catégorie
(tokens `cat-*`), menu ⋯, chevron ; CTA +Nouveau ▾. Préserver attache/détache, partages
(communauté `is_public`, classe `groupService.shareBinder`), owner vs read-only, stats binder.
Feuilles ré-agencées avec `PageHeader` : `Notes`, `NoteEdit` (zen, ~68ch), `PdfReader`, `Diagrams`.
Ajouter tokens `cat-*` si absents.

> **État S3 (🔄)** : cœur fait — `Reviews.vue` (route `reviser`) passé en `PageContainer`+`PageHeader`,
> sélecteurs catégories/sous-onglets tokenisés (dans `#actions`), **bandeau « À réviser maintenant »**
> branché sur le store `focus` (totalDue/lateCount, CTA « Tout réviser » → `startUnifiedReview`) et
> **entrée Examen** (→ `/exam/setup`) intégrée (anti-stranding S0 retiré). **Reste (S7)** : onglet
> Flashcards en `ListRow` (Étudier/Stats/⋯) et re-skin des corps d'onglets IA + runners.

## Lot S3 — Réviser (file due + modes en onglets)

`Reviews.vue`→ vue **Réviser** (route `reviser`) : bandeau « À réviser maintenant » + CTA « Tout
réviser » ; `PageHeader`+`Tabs` (Flashcards SM-2/QCM-Typés/Feuille blanche IA/Examen) en gardant le
contenu Classiques/IA. Onglet Flashcards = gestion des decks en `ListRow` (Étudier/Stats/⋯). Onglet
Examen = carte → `/exam/setup`. Runners ré-agencés (routes inchangées) : `StudyDeck`/`QcmRun`/
`RevisionStudy` ; `ExamSetup`/`ExamSession`(immersif)/`ExamResults`.

> **État S4 (🔄)** : `ClassesLanding` (coquille S0) inchangée. **Migrés** : `StudentClassView`
> (sous-en-tête + stats + devoirs par statut → tokens success/danger/info, Q&A) et `GroupsList`
> (cartes + modales `BaseModal`, violet→primary) — wrappers page autonomes retirés (montés dans
> `ClassesLanding`). **Restent (S7)** : `TeacherDashboard` (1064 l, 136 couleurs brutes),
> `GroupDetail`, `AssignmentDetail`/`AssignmentBuilder` — gros/complexes, migration prudente.

## Lot S4 — Classes (fusion réelle Teacher/Student/Groups)

Étendre `ClassesLanding` : harmoniser `TeacherDashboard` (sous-onglets Devoirs/Ressources/
Progression/Analytics/Roster/Q&A), `StudentClassView` (devoirs par statut, Q&A, stats), `GroupsList`/
`GroupDetail`. Feuilles `AssignmentDetail`/`AssignmentBuilder` avec `PageHeader`.

## Lot S5 — Planning (allégé)

`PlanningPage` : `PageContainer`+`PageHeader` (Tabs Semaine/Mois + action Avancer) ; `MonthCalendar`/
`WeekCalendar` ré-agencés ; store `planning` inchangé.

> **État S6 (🔄)** : **migrés** — `PublicLayout` (coquille : header/footer tokenisés, logo/CTA
> indigo→primary, « Espace personnel »→`/accueil` déjà OK), `Marketplace/Home` (landing : hero +
> 6 cartes feature via tokens `cat-*`/sémantiques + stats), `Marketplace/Explore` (recherche +
> grilles packs/cours en `BaseCard`, follow done→success). **Restent (S7)** : `PackagePreview` et
> `Notes/PublicNote` (pages de détail). clone/follow inchangés.

## Lot S6 — Communauté / Public

`PublicLayout` (header simplifié, « Espace personnel »→`/accueil`) ; `Marketplace/Home|Explore|
PackagePreview`, `Notes/PublicNote` en `PageHeader`/`BaseCard`/`ListRow` ; clone/follow inchangés.

> **État S7 (🔄)** : **faits** — `Marketplace/PackagePreview` et `Notes/PublicNote` tokenisés
> (chrome ; le HTML de rendu markdown de `PublicNote` — placeholders QCM/VF à couleurs
> fonctionnelles — laissé tel quel) ; `prefers-reduced-motion` déjà présent (`style.css`) ;
> `/binders`→`/bibliotheque` post-clone corrigé. `GroupDetail` + `AssignmentDetail` aussi réécrits
> en tokens (statuts/scores/rôles sémantiques ; back→`/classes?tab=teacher`). `AssignmentBuilder`
> (modale création devoir) aussi migré (amber→primary).
> **Lot S8** : `TeacherDashboard` migré en tokens (amber/orange marque→`primary` ; amber statut→
> `warning` ; gamification→`accent` ; vert/rouge/bleu+indigo→`success`/`danger`/`info` ; barres
> en cours→`primary`, terminé→`success` ; slate→`ink`/`surface`/`line`). Bug pré-existant corrigé
> au passage : classes Tailwind invalides (`slate-455/350/105/750`, `green-650`, `blue-650`).
> **Restent — à faire avec VÉRIFICATION VISUELLE HUMAINE** (complexes/fonctionnels) :
> `NoteEdit` (mode zen),
> corps éditeur `Diagrams` (couleurs nœuds en data), onglet Flashcards de `Reviews` en `ListRow` +
> corps onglets IA + runners ; puis **audits transverses** (dark mode, contraste AA des pastels,
> responsive 375 px, smoke test Capacitor).

## Lot S7 — Finition (audit transverse)

Revue feuilles (zen/runners/examen) ; audit dark mode + responsive 375 px + contraste AA pastels ;
`prefers-reduced-motion` ; nettoyage vues/routes mortes + code anti-stranding ; smoke test Capacitor
(`npm run build && npx cap sync` ; envisager bottom-tab bar mobile 5 sections) ; MAJ docs + journal.
**Vérif finale** : les 12 anciennes entrées toutes atteignables depuis les 5 sections ; build+tests
verts ; aucun lien cassé ; modes spéciaux intacts.
