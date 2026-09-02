<template>
  <BaseModal :open="true" size="lg" @close="$emit('close')">
    <template #title>
      <span class="flex items-center gap-2">
        <HelpCircle class="w-5 h-5 text-primary" />
        Guide d'utilisation StudyHub
      </span>
    </template>

    <div
      class="space-y-5 overflow-y-auto text-xs text-ink-muted dark:text-ink-subtle leading-relaxed pr-1 max-h-[60vh]"
    >
      <!-- Section 1: Placeholders -->
      <div class="space-y-2">
        <h4
          class="font-bold text-ink dark:text-white text-xs uppercase tracking-wider font-semibold"
        >
          1. Syntaxes de Révision Intégrée (Active Reading)
        </h4>
        <p>
          Incorporez des questions interactives de révision directe dans vos notes Markdown.
          Révisez-les en place via le mode « Révision Active » ; elles alimentent aussi les
          évaluations IA générées depuis la note :
        </p>
        <ul class="list-disc pl-5 space-y-2.5 mt-1">
          <li>
            <strong class="text-primary dark:text-primary">Texte à trous (Cloze) :</strong>
            Utilisez <code v-pre>{{trou::mot caché}}</code
            >.
            <p class="text-tiny text-ink-muted mt-0.5">
              Exemple : La capitale de la France est <code v-pre>{{ trou::Paris }}</code
              >.
            </p>
          </li>
          <li>
            <strong class="text-primary dark:text-primary"
              >Question à choix multiples (QCM) :</strong
            >
            Utilisez
            <code v-pre>{{qcm::Question ?::Option1|*Bonne Option*|Option3}}</code>
            (entourez la bonne option d'astérisques).
            <p class="text-tiny text-ink-muted mt-0.5">
              Exemple : <code v-pre>{{qcm::Combien de continents ?::4|5|*6|7*|8}}</code
              >.
            </p>
          </li>
          <li>
            <strong class="text-primary dark:text-primary">Ordre / Séquence :</strong>
            Utilisez
            <code v-pre>{{ordre::Titre::Étape 1 > Étape 2 > Étape 3}}</code> (étapes séparées par
            <code>></code>).
            <p class="text-tiny text-ink-muted mt-0.5">
              Exemple :
              <code
                v-pre
                >{{ordre::Cycle de l'eau::Évaporation > Condensation > Précipitations}}</code
              >.
            </p>
          </li>
          <li>
            <strong class="text-primary dark:text-primary">Associations :</strong>
            Utilisez
            <code v-pre>{{assoc::Titre::Clé 1=Valeur 1 | Clé 2=Valeur 2}}</code> (paires
            <code>clé=valeur</code> séparées par <code>|</code>).
            <p class="text-tiny text-ink-muted mt-0.5">
              Exemple : <code v-pre>{{assoc::Capitales::France=Paris | Italie=Rome}}</code
              >.
            </p>
          </li>
          <li>
            <strong class="text-primary dark:text-primary">Vrai / Faux :</strong>
            Utilisez
            <code v-pre>{{ vf::Affirmation::Vrai / Faux::Justification }}</code>
            (séparateur <code>::</code>).
            <p class="text-tiny text-ink-muted mt-0.5">
              Exemple :
              <code v-pre>{{vf::La Terre est plate::Faux::Elle a la forme d'un géoïde.}}</code
              >.
            </p>
          </li>
        </ul>
      </div>

      <!-- Section 2: Split Screen -->
      <div class="space-y-2 border-t border-line dark:border-line pt-4">
        <h4
          class="font-bold text-ink dark:text-white text-xs uppercase tracking-wider font-semibold"
        >
          2. Écran Partagé & Liaisons PDF
        </h4>
        <p>Étudiez vos PDF de cours tout en rédigeant ou révisant vos notes :</p>
        <ul class="list-disc pl-5 space-y-2.5 mt-1">
          <li>
            <strong class="text-primary dark:text-primary">Démarrer l'écran partagé :</strong>
            Sélectionnez un document PDF dans la liste déroulante
            <strong class="text-ink dark:text-white font-semibold">"Aperçu PDF"</strong>
            en haut à droite de l'éditeur de notes. Le PDF s'affichera à gauche.
          </li>
          <li>
            <strong class="text-primary dark:text-primary">Créer une citation (Deep Link) :</strong>
            Sélectionnez du texte dans le panneau PDF, puis cliquez sur le bouton
            <strong class="text-primary dark:text-primary">"Citer"</strong> qui apparaît au-dessus
            du texte. Cela insère un lien spécial de type <code v-pre>pdf://</code> dans votre note.
          </li>
          <li>
            <strong class="text-primary dark:text-primary">Naviguer à partir d'un lien :</strong>
            Dans le mode visualisation de la note, cliquez sur un de vos liens de citation. Le PDF
            s'ouvrira automatiquement sur la bonne page et la zone correspondante sera surlignée.
          </li>
        </ul>
      </div>

      <!-- Section 3: Image Occlusion -->
      <div class="space-y-2 border-t border-line dark:border-line pt-4">
        <h4
          class="font-bold text-ink dark:text-white text-xs uppercase tracking-wider font-semibold"
        >
          3. Masques d'Image (Occlusion)
        </h4>
        <p>
          Dans le module
          <strong class="text-ink dark:text-white font-semibold">Diagrammes</strong>, importez un
          schéma (corps humain, géographie, formule), tracez des rectangles de masquage opaques sur
          les parties à deviner, puis nommez-les. En mode révision, cliquez sur les masques pour les
          révéler et évaluer votre mémorisation.
        </p>
      </div>

      <!-- Section 4: Tableaux & sauts de ligne -->
      <div class="space-y-2 border-t border-line dark:border-line pt-4">
        <h4
          class="font-bold text-ink dark:text-white text-xs uppercase tracking-wider font-semibold"
        >
          4. Tableaux & sauts de ligne
        </h4>
        <p>
          Dans un tableau Markdown, chaque ligne du texte correspond à une ligne du tableau : une
          simple touche
          <kbd
            class="px-1.5 py-0.5 rounded bg-surface-soft dark:bg-surface-soft border border-line text-tiny font-mono"
            >Entrée</kbd
          >
          casserait donc la ligne. Pour aller à la ligne
          <strong class="text-ink dark:text-white font-semibold">à l'intérieur d'une cellule</strong
          >, utilisez
          <kbd
            class="px-1.5 py-0.5 rounded bg-surface-soft dark:bg-surface-soft border border-line text-tiny font-mono"
            >Maj</kbd
          >
          +
          <kbd
            class="px-1.5 py-0.5 rounded bg-surface-soft dark:bg-surface-soft border border-line text-tiny font-mono"
            >Entrée</kbd
          >
          (insère un retour à la ligne propre). Cela fonctionne aussi partout ailleurs pour un saut
          de ligne souple.
        </p>
      </div>
    </div>

    <template #footer>
      <BaseButton @click="$emit('close')">Compris !</BaseButton>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { HelpCircle } from '@lucide/vue'
import { BaseModal, BaseButton } from '../ui/base'

defineEmits<{ close: [] }>()
</script>
