# Spec — Écran 4 (Éditeur de notes & mode Zen) vers Direction A

## Décision utilisateur (2026-08-25)

> « j'aimerais garder les fonctionnalités mais refaire l'interface et appliquer le thème »

En réponse à la question posée après lecture de la vraie maquette `NoteEdit.dc.html` : la
maquette montre un écran radicalement plus simple (chrome standard, pas de mode Zen, pas de
double panneau live preview, pas de barres LaTeX/Code séparées, pas de tiroir Contexte/Liens,
pas de partage public, pas d'export PDF, pas de moteur de syntaxes de révision active, pas de
modale SM-2) que le code réel (`web/src/views/Notes/NoteEdit.vue`, 3025 lignes). Décision :
**zéro fonctionnalité supprimée** ; la maquette sert d'inspiration visuelle (breadcrumb, carte
« Assistant IA », carte « Métadonnées », esthétique des boutons) appliquée par-dessus
l'architecture fonctionnelle actuelle, pas une refonte structurelle qui l'appauvrirait.

## Inventaire exhaustif de l'existant (lecture complète du fichier, 2026-08-25)

### Éléments d'interface / actions par zone

**Bannière lecture seule** (note partagée par un cours, `isReadOnly`) : icône, texte, bouton
« Cacher » (`hideFromView`), bouton « Copier pour modifier » (`copyForEditing`, état
`isCopying`).

**Mode édition (`isEditMode`) — Row 1 (en-tête)** :
- Bouton bascule tiroir raccourcis (`toggleShortcutSidebar`, dispatch `studyhub:toggle-sidebar`)
- Champ titre inline (`v-model="title"`, `@input="triggerAutoSave"`)
- Statut de sauvegarde (pastille + texte `saveStatus` : Enregistré/Modifications.../
  Sauvegarde.../Sauvegardé/Erreur)
- Sélecteur classeur (`v-model="binderId"`, options `bindersStore.binders` + « Général (Aucun) »)
- `TagSelector` (compact, `v-model="noteTags"`, `@change="saveNoteTags"`)
- Bouton « Contexte / Liens » (`showSettings` toggle, ouvre le tiroir ci-dessous)
- Bouton « Aperçu » (`isLivePreviewActive` toggle, double panneau live)
- Bouton « Visualiser » (`toggleMode` → bascule vers mode lecture)
- Bouton Partage : « Public »/« Privé » (`handleShareClick` → `togglePublic` si privé, toggle
  popup si déjà public) + popup (lien `shareUrl`, bouton Copier `copyShareLink` avec état
  `shareCopied`, bouton « Rendre privée » → `togglePublic`)
- Bouton « Guide » (`showHelpModal = true`)

**Mode édition — Row 2 (barre de formatage)** :
- 4 boutons Format (`formatButtons` : Titre H1/H2, Gras, Italique) → `insertText(prefix, suffix)`
- 5 boutons LaTeX (`latexButtons` : Bloc Équation, En Ligne, Fraction, Somme, Intégrale) →
  `insertText`
- 2 boutons Code (`codeButtons` : En Ligne, Bloc Code) → `insertText`
- Bouton « Définition (Info-bulle) » → `insertDefinitionTooltip` (ouvre `NoteInputModal` si
  aucune sélection, sinon insère directement)
- Sélecteur « Insérer un diagramme... » (`allUserDiagrams`) → `insertDiagramTag`

**Mode édition — tiroir Contexte/Liens (`showSettings`)** :
- Textarea contexte (`v-model="noteContext"`, `@input="triggerAutoSave"`)
- Sélecteur + bouton « Lier » pour notes liées (`selectedLinkTarget`, `linkableNotes`,
  `addNoteLink`)
- Badges des notes liées (`noteLinks`, bouton retirer par badge `removeNoteLink`)

**Mode édition — zone de saisie** :
- `textarea` markdown (`v-model="noteBody"`, `@input`, `@mouseup`/`@keyup` →
  `handleTextareaSelect`, `@keydown.tab.prevent="handleTabKey"`,
  `@keydown.enter.shift.prevent="insertSoftBreak"`)
- Panneau live preview optionnel (`isLivePreviewActive`, rendu `renderMarkup(noteBody)`)

**Mode édition — barre d'action flottante sur sélection (`showSelectionMenu`)** : 10 boutons de
transformation (`applySelectionTransform` : trou, qcm, ordre, assoc, vf, def, math_bloc,
math_ligne, diagramme, gras, italique, code, bloc_code — 13 en réalité). QCM/Ordre/Assoc/VF/Def/
Diagramme ouvrent `openModal` (modale générique de saisie) avant d'insérer.

**Mode lecture (`!isEditMode`) — barre d'action** :
- Bouton retour (`goBack`, libellé « Retour aux notes »)
- Bascule Lecture/Révision Active (`notesStore.isReviewModeActive`)
- Bouton « Réviser avec l'IA » → `showAiModal = true` (modale 3 activités : Blurting/Quiz/
  Évaluation → `startAiActivity(type)`, navigation `/notes/:id/:type`)
- Bouton « Modifier la fiche » (`toggleMode`)
- Bouton « Guide » (`showHelpModal`)
- Bouton « Exporter en PDF » (`printNote` → `showPdfModal = true` → `NotePdfExportModal`
  existant, `@export="handlePdfExport"`)

**Mode lecture — feuille de contenu** :
- Bannière d'en-tête imprimable (conditionnelle `pdfExportOptions.includeHeader`)
- Titre + classeur (badge) + tags (`TagBadge`)
- Sommaire imprimable (`pdfExportOptions.includeToc`)
- Bloc Contexte (`noteContext`, si `pdfExportOptions.includeContext`)
- Bloc Définitions legacy (`noteDefinition`)
- Contenu principal rendu (`renderMarkup(noteBody)`, clic → `handleMarkdownClick` →
  `handlePlaceholderInteraction`)
- Glossaire imprimable (`pdfExportOptions.includeGlossary`)
- Notes liées (boutons de navigation `navigateToNote`)
- Pied de page imprimable (`pdfExportOptions.includeFooter`)

**Modales** (4, toutes actuellement en HTML/CSS bruts dupliqués, à unifier sur `BaseModal`) :
1. Aide (`showHelpModal`) — contenu statique (4 sections : placeholders, écran partagé PDF,
   masques d'image, tableaux/sauts de ligne).
2. Activités IA (`showAiModal`) — 3 cartes cliquables (`aiActivities`).
3. Saisie générique (`inputModal`, remplace prompt/confirm/alert) — champs `text`/`bool`/
   `select` dynamiques, utilisée par `applySelectionTransform` (def/qcm/ordre/assoc/vf/
   diagramme) et `insertDefinitionTooltip`.
4. Évaluation SM-2 (`evaluationModal`) — 4 boutons notation (`evaluationButtons`) →
   `submitSm2Evaluation(score)`.

**Rendu markup (`renderMarkup`)** — moteur de syntaxes de révision active, injecté via
`v-dompurify-html` (HTML généré en chaînes JS, pas des composants Vue) :
- LaTeX bloc/inline (KaTeX)
- Info-bulles de définition (`[terme]{def:...}`)
- Diagrammes (`[diagram:ID]`, `renderDiagramHtml` — schéma visuel avec nœuds/connexions/masques
  d'occlusion SVG, ou fallback Mermaid texte)
- Trou (`{{trou::mot}}`), QCM (`{{qcm::Q::opts}}`), Vrai/Faux (`{{vf::...}}`),
  Ordre (`{{ordre::titre::étapes}}`), Association (`{{assoc::titre::paires}}`) — chacun avec
  vue statique (hors révision) et vue interactive (`notesStore.isReviewModeActive`), boutons
  `renderSm2Buttons` une fois noté.
- Interactions déléguées à `handlePlaceholderInteraction` via délégation d'événement
  (`data-action` sur les éléments générés) : reveal, qcm-select, vf-select, order-move/validate,
  assoc-key-select/value-select/remove/validate, sm2-vote, sm2-re-evaluate.

**Appels API** : `notesStore.fetchNoteById`, `notesStore.updateNote`, `notesStore.copyNote`,
`notesStore.hideNote`, `api.patch('/notes/:id/visibility')`, `api.patch('/flashcards/:id/review')`,
`api.get('/diagrams?per_page=1000')`, `api.get('/diagrams/:id')`, `bindersStore.fetchBinders`,
`tagsStore.fetchTags`/`setTagsForEntity`, `notesStore.fetchNotes`.

**Mode Zen** (`AppLayout.vue`, `isZenMode = route.name === 'NoteEdit'`) : sidebar devient overlay
survol, en-tête se masque et réapparaît au survol d'une bande invisible en haut. **Conservé tel
quel** — fonctionnalité réelle, non couverte par la maquette (qui montre un chrome standard),
traitée comme un ajout légitime du produit au même titre que les widgets réels de l'Accueil
absents de sa maquette.

## États à couvrir (skill `migration-ecran` étape 2)

- **Chargement** : déjà présent (spinner + texte) — à couvrir par un test.
- **Vide** : note neuve (`noteBody` vide) → l'éditeur reste utilisable, aucun cas particulier
  (le placeholder du textarea suffit). Classeur/tags absents → « Général (Aucun) », pas de tags.
  Aucune note liée → section masquée. Aucun diagramme utilisateur → option désactivée dans le
  sélecteur d'insertion + modale de garde dans `applySelectionTransform('diagramme')` (déjà
  gérée).
- **Erreur** — **lacune réelle trouvée, même famille que les écrans 2 et 3** :
  `loadNoteDetails()` n'a aucun `try/catch` — un échec de `notesStore.fetchNoteById` fait
  planter le montage sans état d'erreur ni retour utilisateur. À corriger : `try/catch` autour
  du chargement, état `loadError` + `BaseEmptyState` (action « Réessayer » → relance
  `loadNoteDetails`), même pattern qu'`Accueil.vue`/`StudyDeck.vue`. `saveNote()` gère déjà son
  échec (`saveStatus = 'Erreur'`) — à couvrir par un test, pas à corriger.
- **Dense** : note très longue, beaucoup de tags, beaucoup de notes liées, beaucoup de
  diagrammes dans le sélecteur — déjà géré par le layout existant (`overflow-y-auto`,
  `flex-wrap`, troncature du sélecteur classeur) ; à couvrir par des tests, pas de nouveau code.
- **Hors ligne** : pas de traitement spécifique à cet écran — un échec réseau au montage tombe
  dans l'état erreur ci-dessus ; l'indicateur hors ligne global (coquille) reste affiché
  indépendamment. L'auto-sauvegarde (`triggerAutoSave`/`saveNote`) qui échoue hors ligne est déjà
  couverte par l'état `saveStatus = 'Erreur'` existant.

## Mapping tokens (couleurs brutes → tokens du projet)

Le fichier utilise massivement des couleurs Tailwind brutes (`slate-*`, `rose-*`, `indigo-*`,
`emerald-*`, `amber-*`, `blue-*`, `purple-*`, `pink-*`, `cyan-*`, `teal-*`, `sky-*`) à la fois
dans le template statique ET dans les chaînes HTML générées par `renderMarkup`/
`renderSm2Buttons`/`evaluationButtons`/`aiActivities`. Mapping à appliquer partout (cohérent avec
la skill `design-system` et les migrations déjà faites sur les écrans 1-3) :

| Usage sémantique | Couleur brute actuelle | Token du projet |
|---|---|---|
| Neutre / fond secondaire | `slate-*`, `gray-*` | `surface-soft`, `ink-subtle`, `ink-muted`, `line` |
| Accent primaire (actions, sélection, indigo) | `indigo-*`, `purple-*`, `blue-*` | `primary`/`primary-soft`/`primary-ink` |
| Succès / validé | `emerald-*`, `green-*` | `success`/`success-soft` |
| Alerte / attention | `amber-*`, `orange-*`, `yellow-*` | `warning`/`warning-soft` |
| Erreur / faux / danger | `rose-*`, `red-*` | `danger`/`danger-soft` |
| Accent secondaire (LaTeX/formule, diagramme) | `cyan-*`, `teal-*`, `sky-*`, `pink-*` | `accent`/`accent-soft` (un seul accent secondaire du design system — pas de nouvelle couleur) |

**Exemption explicite** : le bloc `<style>` `@media print` (lignes ~2766-2944) reste en couleurs
brutes (`#0f172a`, `#cbd5e1`, etc.) — le PDF exporté doit toujours rendre sur papier blanc,
indépendamment du thème clair/sombre de l'application. Ce n'est pas un token de l'app, c'est une
palette d'impression figée intentionnellement. Ne pas y toucher.

## Composants à extraire (fichier actuel : 3025 lignes, bien au-delà du seuil de lisibilité)

| Fichier | Contenu | Primitives utilisées |
|---|---|---|
| `web/src/components/notes/NoteEditHelpModal.vue` | Modale Guide (statique) | `BaseModal` |
| `web/src/components/notes/NoteInputModal.vue` | Modale de saisie générique (remplace prompt/confirm/alert) | `BaseModal`, `BaseField`, `BaseInput`, `BaseButton` |
| `web/src/components/notes/NoteEvaluationModal.vue` | Modale évaluation SM-2 | `BaseModal`, `BaseButton` |
| `web/src/components/notes/NoteSidebar.vue` | Nouveau : carte « Assistant IA » (remplace la modale IA) + carte « Métadonnées » (classeur/tags/modifiée), mode lecture uniquement | `BaseCard`, `BaseBadge` |
| `NoteEdit.vue` (fichier principal) | Reste : en-tête édition/lecture, barres de formatage, tiroir contexte/liens, zone de saisie, feuille de lecture, moteur `renderMarkup`, logique métier | `BaseButton`, `BaseBadge`, `Tabs` (bascule Lecture/Révision Active), `BaseCard` |

**Décision explicite : la modale Activités IA (`showAiModal`/`aiActivities`) est retirée** — ses
3 actions (Blurting/Quiz/Évaluation, même fonction `startAiActivity`) deviennent la carte
persistante « Assistant IA » de `NoteSidebar.vue`, visible en permanence en mode lecture au lieu
d'être cachée derrière une modale. Aucune action perdue, juste plus directement accessible —
c'est la seule idée structurelle de la maquette qui améliore réellement l'existant sans rien
retirer. Le bouton d'en-tête « Réviser avec l'IA » est retiré (redondant avec la carte toujours
visible dans la colonne latérale).

**Toolbar de formatage (Row 2)** : reste en boutons texte (pas d'icônes) — reconnaître un bouton
« Fraction »/« Intégrale »/« Somme » à une icône générique serait ambigu et risquerait de nuire à
la découvrabilité ; restylée avec les tokens (`BaseButton variant="ghost" size="sm"`) plutôt que
recomposée en icônes comme le suggère la maquette (5 boutons génériques Gras/Italique/Titre/
Liste/Formule) — la maquette n'a pas à couvrir ce niveau de détail (LaTeX à 5 variantes, Code à 2
variantes) qu'elle ignore complètement.

**Breadcrumb** (ajout inspiré de la maquette, additif, aucune fonctionnalité retirée) : mode
lecture uniquement, `Bibliothèque / {classeur} / Notes` au-dessus du titre, classeur = nom réel
via `getBinderName(binderId)` (déjà disponible), lien statique (pas de navigation ajoutée —
hors périmètre).

## Non négociables (skill `migration-ecran`)

Contraste AA, cibles tactiles ≥44px, `safe-area-inset` iOS (mode Zen), `prefers-reduced-motion`
sur les transitions ajoutées/modifiées. Aucun token ni primitive à créer — tout existe déjà
(`BaseModal`, `BaseCard`, `BaseButton`, `BaseBadge`, `BaseField`, `BaseInput`, `Tabs`).
