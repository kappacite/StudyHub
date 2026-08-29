// Seuil unique de banding "taux de reussite / maitrise" (0-100), partage par
// toutes les vues qui colorent une valeur de succes -- une seule echelle a 2
// paliers (succes/echec), pour eviter que plusieurs pages inventent chacune
// leur propre seuil (cf. chantier reviser-hub, tache 5 : trois schemas
// incoherents trouves puis unifies sur >=70 -- ce seuil vit ici pour que la
// prochaine vue le reutilise au lieu d'en recreer un).
export const SUCCESS_RATE_THRESHOLD = 70

export function successRateTextClass(rate: number): string {
  return rate >= SUCCESS_RATE_THRESHOLD ? 'text-success' : 'text-danger'
}

export function successRateBgClass(rate: number): string {
  return rate >= SUCCESS_RATE_THRESHOLD ? 'bg-success' : 'bg-danger'
}
