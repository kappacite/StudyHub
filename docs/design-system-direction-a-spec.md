# StudyHub — Direction A « Fiche » — spec partagée pour toutes les maquettes

Direction retenue par l'utilisateur (arbitrage reçu). Tous les écrans ci-dessous doivent
utiliser **exactement** ce langage visuel — aucune variation de palette/typo d'un écran
à l'autre. Réutilise les blocs ci-dessous tels quels (copie-colle, adapte le contenu).

Référence vivante à consulter si besoin : `Main.dc.html` dans ce même dossier (écran
Accueil déjà construit dans cette direction).

## Palette (variables CSS, thème clair + sombre)

```css
.theme-light {
  --bg: #EFEAE0;
  --surface: #FBF8F2;
  --ink: #23241F;
  --ink-muted: #6B6858;
  --accent: #2E4374;        /* encre indigo — actions primaires, liens, "Bien" en SM2 */
  --accent-ink: #FFFFFF;    /* texte sur fond accent */
  --highlight: #C99A2E;     /* rehaut ocre — échéance du jour, "Difficile" en SM2 */
  --highlight-soft: #EADFC0;
  --line: #D9D0BC;          /* filets, séparateurs pointillés */
  --danger: #B24C3A;        /* brique — suppression, "Encore" en SM2 */
  --danger-soft: #E7CFC6;
  --success: #5C7A5A;       /* sauge — "Facile" en SM2 */
  --success-soft: #D9E0D3;
  --shadow: 0 1px 2px rgba(35,36,31,0.06), 0 8px 20px -12px rgba(35,36,31,0.18);
}
.theme-dark {
  --bg: #1B1912;
  --surface: #242119;
  --ink: #F3EFE3;
  --ink-muted: #B8B29C;
  --accent: #93A9DE;
  --accent-ink: #1B1912;
  --highlight: #E0B84A;
  --highlight-soft: #3A311C;
  --line: #3A3627;
  --danger: #E08872;
  --danger-soft: #3D2A22;
  --success: #8FAE8B;
  --success-soft: #26301F;
  --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 24px -12px rgba(0,0,0,0.5);
}
```

Ces deux blocs vont TELS QUELS dans le `<style>` de `<helmet>` de chaque fichier.

## Typographie

Google Fonts (lien à mettre dans `<helmet>`, avant le `<style>`) :
```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bitter:wght@400;600;700&family=Karla:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap">
```
- **Display** (`class="display"`, `font-family:'Bitter',Georgia,serif`) : titres de page (30px/700),
  titres de carte (17-19px/700). Utilisé avec retenue — jamais pour le corps de texte.
- **Corps** (`'Karla',system-ui,sans-serif`, par défaut sur le body) : tout le texte courant.
  Tailles : 16px (lecture longue — note, énoncé), 14px (UI standard), 13px (secondaire), 12px (labels).
- **Données/méta** (`class="mono"`, `'Space Mono','Courier New',monospace`) : nombres, dates,
  compteurs, timestamps, statuts brefs. Toujours en petites tailles (9-13px).

## Rayons, ombre, espacement

- Cartes : `border-radius:8px` + `box-shadow:var(--shadow)` (classe `.card`).
- Boutons primaires : `border-radius:10px`. Boutons secondaires/inputs : `border-radius:8px`.
  Puces/pills/badges : `border-radius:999px`. Coins "fiche bristol" (bandeau hero, tab) : `4px`.
  Cases à cocher : `border-radius:3px`.
- Échelle d'espacement (px) : 4, 8, 12, 16, 20, 24, 28, 32, 40, 48 — jamais de valeur hors échelle.
- Séparateurs internes (listes) : `border-bottom:1px dashed var(--line)` (effet "ligne de cahier"),
  jamais un trait plein sauf sur les contours de carte/nav (`1px solid var(--line)`).

## Bloc CSS de base (à inclure dans chaque `<helmet><style>`, en plus des blocs thème ci-dessus)

```css
* { box-sizing: border-box; }
body { margin: 0; }
a { color: var(--accent); }
a:hover { color: var(--highlight); }
.mono { font-family: 'Space Mono', 'Courier New', monospace; }
.display { font-family: 'Bitter', Georgia, serif; }
.pill { display: inline-flex; align-items: center; gap: 6px; padding: 7px 16px; border-radius: 999px; font-size: 13px; font-weight: 600; }
.card { background: var(--surface); border-radius: 8px; box-shadow: var(--shadow); }
```

## Tweak thème clair/sombre — OBLIGATOIRE sur CHAQUE artboard

Chaque fichier a EXACTEMENT ce script (adapter uniquement si l'écran a d'autres besoins d'état) :

```html
<script data-dc-script data-props='{"dark":{"editor":"boolean","default":false}}'>
class Component extends DCLogic {
  renderVals() {
    const dark = this.state.dark ?? this.props.dark ?? false;
    return {
      theme: dark ? 'dark' : 'light',
      toggleTheme: () => this.setState({ dark: !dark })
    };
  }
}
</script>
```
Et le conteneur racine : `<div class="app-root theme-{{theme}}" style="min-height:...px; background:var(--bg); color:var(--ink); font-family:'Karla',system-ui,sans-serif;">`.
Le bouton de bascule (voir nav ci-dessous) porte `onClick="{{toggleTheme}}"`.

## Nav desktop (coquille applicative — à réutiliser telle quelle en haut de CHAQUE écran "app", pas les écrans publics/auth)

```html
<header style="display:flex; align-items:center; justify-content:space-between; padding:18px 40px; border-bottom:1px solid var(--line);">
  <div style="display:flex; align-items:center; gap:36px;">
    <span class="display" style="font-weight:700; font-size:19px; letter-spacing:-0.01em;">StudyHub</span>
    <nav style="display:flex; align-items:center; gap:4px;">
      <span class="pill" style="background:var(--accent); color:var(--accent-ink);">[Item actif]</span>
      <span class="pill" style="color:var(--ink-muted);">Accueil</span>
      <span class="pill" style="color:var(--ink-muted);">Bibliothèque</span>
      <span class="pill" style="color:var(--ink-muted);">Réviser</span>
      <span class="pill" style="color:var(--ink-muted);">Classes</span>
      <!-- retire l'item qui correspond a "actif" de cette liste de 4, il est deja rendu en pill active plus haut -->
    </nav>
  </div>
  <div style="display:flex; align-items:center; gap:18px;">
    <button onClick="{{toggleTheme}}" style="cursor:pointer; width:34px; height:34px; border-radius:8px; border:1px solid var(--line); background:var(--surface); display:flex; align-items:center; justify-content:center; padding:0;" aria-label="Basculer le theme">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--ink-muted)" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"></circle><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"></path></svg>
    </button>
    <div style="width:34px; height:34px; border-radius:50%; background:var(--accent); color:var(--accent-ink); display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700;" class="mono">CM</div>
  </div>
</header>
```
Largeur de cadre desktop standard : **1280px**, contenu principal dans `<main style="padding:40px; display:flex; flex-direction:column; gap:28px;">`.

## Nav mobile (barre basse + mini-header — pour les écrans mobiles uniquement)

Mini-header (52px) :
```html
<header style="display:flex; align-items:center; justify-content:space-between; padding:0 16px; height:52px; border-bottom:1px solid var(--line); flex-shrink:0;">
  <span class="display" style="font-weight:700; font-size:16px;">StudyHub</span>
  <div style="display:flex; align-items:center; gap:10px;">
    <button onClick="{{toggleTheme}}" style="cursor:pointer; width:32px; height:32px; border-radius:8px; border:1px solid var(--line); background:var(--surface); display:flex; align-items:center; justify-content:center; padding:0;">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--ink-muted)" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"></circle><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"></path></svg>
    </button>
    <div style="width:28px; height:28px; border-radius:50%; background:var(--accent); color:var(--accent-ink); display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:700;" class="mono">CM</div>
  </div>
</header>
```
Barre basse fixe (64px + safe-area), 4 onglets `Accueil / Bibliothèque / Réviser / Classes` :
```html
<nav style="display:flex; align-items:center; justify-content:space-around; height:64px; padding-bottom:env(safe-area-inset-bottom,0px); background:var(--surface); border-top:1px solid var(--line); flex-shrink:0;">
  <div style="display:flex; flex-direction:column; align-items:center; gap:3px; min-width:44px; min-height:44px; justify-content:center; color:var(--accent);">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-7 9 7"></path><path d="M5 10v9a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1v-9"></path></svg>
    <span style="font-size:10px; font-weight:600;">Accueil</span>
  </div>
  <!-- 3 autres onglets identiques, color:var(--ink-muted) si inactif, icone differente (livre pour Bibliotheque, flamme pour Reviser, gens pour Classes) -->
</nav>
```
Cadre mobile standard : **largeur 390px**, `<div class="app-root theme-{{theme}}" style="width:390px; display:flex; flex-direction:column; min-height:844px;">` avec header en haut, `<main style="flex:1; overflow-y:auto; padding:20px 16px; display:flex; flex-direction:column; gap:20px;">` au milieu, nav en bas — toujours dans cet ordre (colonne flex).

## Boutons

Primaire :
```html
<button style="cursor:pointer; display:flex; align-items:center; gap:9px; padding:12px 22px; border:none; border-radius:10px; background:var(--accent); color:var(--accent-ink); font-family:'Karla'; font-size:14px; font-weight:700;">Libellé</button>
```
Secondaire : mêmes dimensions, `background:var(--surface); border:1px solid var(--line); color:var(--ink);`.
Destructeur : `background:transparent; border:1px solid var(--danger); color:var(--danger);`.

## 4 boutons de notation SM2 (revision de fiches — jamais la couleur seule : icone + libelle obligatoires)

```html
<div style="display:grid; grid-template-columns:repeat(4,1fr); gap:10px;">
  <button style="cursor:pointer; display:flex; flex-direction:column; align-items:center; gap:6px; padding:14px 8px; border-radius:10px; border:1.5px solid var(--danger); background:transparent; color:var(--danger); font-family:'Karla'; font-size:12px; font-weight:700;">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--danger)" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"></path></svg>
    Encore
  </button>
  <button style="cursor:pointer; display:flex; flex-direction:column; align-items:center; gap:6px; padding:14px 8px; border-radius:10px; border:1.5px solid var(--highlight); background:transparent; color:var(--highlight); font-family:'Karla'; font-size:12px; font-weight:700;">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--highlight)" stroke-width="2" stroke-linecap="round"><path d="M4 12h16M4 12l4-4M4 12l4 4"></path></svg>
    Difficile
  </button>
  <button style="cursor:pointer; display:flex; flex-direction:column; align-items:center; gap:6px; padding:14px 8px; border-radius:10px; border:none; background:var(--accent); color:var(--accent-ink); font-family:'Karla'; font-size:12px; font-weight:700;">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-ink)" stroke-width="2" stroke-linecap="round"><path d="M5 13l4 4L19 7"></path></svg>
    Bien
  </button>
  <button style="cursor:pointer; display:flex; flex-direction:column; align-items:center; gap:6px; padding:14px 8px; border-radius:10px; border:1.5px solid var(--success); background:transparent; color:var(--success); font-family:'Karla'; font-size:12px; font-weight:700;">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="2" stroke-linecap="round"><path d="M5 13l4 4L19 7M13 13l4 4L27 7"></path></svg>
    Facile
  </button>
</div>
```

## Carte "ligne de liste" avec indicateur d'échéance (reprend le motif Accueil)

```html
<div style="display:flex; align-items:center; gap:14px; padding:13px 0; border-bottom:1px dashed var(--line);">
  <div style="width:3px; align-self:stretch; background:var(--highlight); border-radius:2px;"></div> <!-- var(--line) si pas urgent -->
  <div style="flex:1; min-width:0;">
    <p style="margin:0; font-size:14px; font-weight:600;">[Titre]</p>
    <p class="mono" style="margin:2px 0 0; font-size:11px; color:var(--ink-muted);">[meta]</p>
  </div>
  <span class="mono" style="font-size:10px; padding:4px 10px; border-radius:999px; background:var(--highlight-soft); color:var(--highlight); font-weight:700; letter-spacing:0.04em;">[STATUT]</span>
</div>
```

## Champ de formulaire

```html
<label style="display:flex; flex-direction:column; gap:6px;">
  <span style="font-size:12px; font-weight:600; color:var(--ink-muted); text-transform:uppercase; letter-spacing:0.03em;">[Label]</span>
  <input type="text" placeholder="[placeholder]" style="font-family:'Karla'; font-size:14px; padding:11px 14px; border-radius:8px; border:1px solid var(--line); background:var(--surface); color:var(--ink); outline:none;" />
</label>
```

## État vide (à utiliser seulement là où c'est pertinent — pas systématique)

```html
<div style="display:flex; flex-direction:column; align-items:center; text-align:center; gap:14px; padding:56px 24px;">
  <div style="width:56px; height:56px; border-radius:50%; border:2px dashed var(--line); display:flex; align-items:center; justify-content:center;">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--ink-muted)" stroke-width="1.6"><!-- icone contextuelle --></svg>
  </div>
  <div>
    <p class="display" style="margin:0 0 4px; font-size:15px; font-weight:700;">[Titre]</p>
    <p style="margin:0; font-size:13px; color:var(--ink-muted); max-width:320px;">[Invitation à agir]</p>
  </div>
  <button style="cursor:pointer; padding:10px 20px; border:none; border-radius:10px; background:var(--accent); color:var(--accent-ink); font-size:13px; font-weight:700;">[Action]</button>
</div>
```

## Icônes

SVG inline uniquement, trait (`stroke`, pas `fill` sauf accents ponctuels), grille 16/20/24px,
`stroke-width` 1.6-2, `stroke-linecap="round"`. Jamais d'émoji.

## Contenu

Français, vocabulaire réel StudyHub (fiches, decks, classeurs, séries de révision, facteur de
facilité SM2, blurting, note, classe/devoir). Données d'exemple plausibles et concrètes (noms de
matières réels : chimie organique, droit constitutionnel, anatomie, espagnol B2, physique
quantique...) — jamais de lorem ipsum, jamais "Titre 1 / Item A". Le produit est un outil
d'étudiants du supérieur qui écrivent des maths en LaTeX et annotent des articles scientifiques :
pas d'infantilisation, pas de ton mignon/enfantin.

## Une seule fiche par écran

Un seul état "peuplé" (pas de variantes loading/error/empty en série pour cette passe de
validation — sauf si l'état vide EST le contenu le plus pertinent à montrer pour cet écran
précis, auquel cas ne montre que celui-là). Chaque écran = un seul artboard desktop 1280px,
sauf mention contraire (mobile en plus) dans la consigne de l'écran.

## Format technique (rappel)

- Garder EXACT `<script src="./support.js"></script>` dans `<head>`.
- Un fichier par écran nommé `<Nom>.dc.html` (ex. `Login.dc.html`), écrit dans ce dossier.
- Pas de TypeScript, pas d'import/export dans le script `data-dc-script`.
- Layout en `display:flex`/`display:grid` + `gap` — jamais de marges entre éléments frères.
- N'appelle PAS le helper de seed/publish — écris seulement les fichiers `.dc.html`. Le
  montage du canevas final est fait de façon centralisée après coup.
