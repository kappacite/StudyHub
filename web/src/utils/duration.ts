// Formatage partage d'une duree exprimee en secondes (Task 9,
// reviser-hub-redesign) -- utilise par RevisionSetStats.vue ("Temps cumulé" +
// colonne "Durée" de l'historique) et RevisionBinderStats.vue ("Temps total
// d'étude"). Ne pas dupliquer cette logique dans une autre vue.
//
// Regle : sous 1h -> "N min" (minutes arrondies) ; a partir de 1h -> "Xh MM"
// (heures entieres + minutes sur 2 chiffres). Le seuil se decide sur le total
// de MINUTES ARRONDI (pas sur les secondes brutes) : une duree qui arrondit a
// 60 min doit basculer en "1h 00", jamais s'afficher "0h 60".
export function formatDuration(seconds: number): string {
  const totalMinutes = Math.round(seconds / 60)
  if (totalMinutes < 60) {
    return `${totalMinutes} min`
  }
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `${hours}h ${String(minutes).padStart(2, '0')}`
}
