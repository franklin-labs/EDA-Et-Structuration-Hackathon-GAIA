# Backend - Moteur de Calcul & Simulation Systémique

Ce document décrit la logique du backend, dont l'objectif principal est de **rapprocher l'exploitation analysée du K-Type (Cas-Type) le plus performant et durable**, en utilisant la **surface en herbe** comme levier principal.

## 1. Objectifs du Moteur

1.  **Identifier le K-Type Cible** : Trouver le système de référence le plus pertinent (proche structurellement mais plus performant écologiquement).
2.  **Calculer la Trajectoire** : Déterminer comment ajuster la variable `surface_herbe` pour converger vers ce modèle.
3.  **Vérifier la Conformité** : S'assurer que chaque étape de la simulation respecte les contraintes réglementaires (Directive Nitrates, PAC, Bien-être animal).

## 2. Modèle de Données (Data Model)

### Entrées (Input)
L'agriculteur ou le conseiller fournit les données structurelles de base :
*   **Filière** (ex: Bovins Lait, Ovins Viande)
*   **SAU** (Surface Agricole Utile, ha)
*   **UGB** (Unités Gros Bétail, nombre)
*   **Part d'Herbe Actuelle** (% de la SAU)
*   **Chargement Actuel** (UGB/ha SFP)

### Sorties (Output)
*   **K-Type Identifié** (ex: "Laitier Intensif Plaine")
*   **K-Type Cible** (ex: "Laitier Herbager Autonome")
*   **Gap Analysis** (Distance à la cible sur les indicateurs clés)
*   **Simulation** (Impact de l'ajustement de l'herbe sur Autonomie, Carbone, Marge)
*   **Alertes Réglementaires** (Booléens + Messages d'avertissement)

## 3. Algorithme de Rapprochement (Matching Logic)

L'algorithme fonctionne en trois étapes :

### Étape A : Identification du Profil Actuel
On utilise une distance euclidienne pondérée pour situer la ferme dans l'espace des K-Types.
$$ Distance(Ferme, KType_i) = \sqrt{ \sum w_j \times (Var_j^{Ferme} - Var_j^{KType_i})^2 } $$
*Variables ($Var_j$)* : Chargement, Part Maïs, Productivité Laitière.

### Étape B : Sélection du K-Type Cible (Targeting)
Le système ne cherche pas le K-Type le plus proche absolu, mais le **K-Type le plus proche ayant une meilleure performance environnementale** (ex: Meilleure autonomie, Moins de Carbone).
*   *Règle* : Si `Ferme.Part_Herbe < 50%`, Cible = `KType_Herbager` (si réalisable pédoclimatiquement).

### Étape C : Simulation du Levier "Surface Herbe"
C'est la variable d'ajustement principale.
1.  L'utilisateur (ou l'algo) propose : `Nouvelle_Part_Herbe = Actuelle + 10%`.
2.  Le moteur recalcule tout le système :
    *   `Nouveau_Maïs` = `Ancien_Maïs` - `Delta_Herbe`
    *   `Nouvelle_Autonomie` = $f(Nouvelle\_Part\_Herbe, Chargement)$
    *   `Nouveau_Carbone` = $f(Intrants, Stockage\_Sol)$

## 4. Prise en Compte des Contraintes Réglementaires

Le moteur intègre un module de vérification ("Compliance Engine") qui s'exécute à chaque simulation.

| Contrainte | Variable Surveillée | Règle de Validation | Action si Violation |
| :--- | :--- | :--- | :--- |
| **Directive Nitrates** | Chargement (UGB/ha) | `Chargement <= 1.7` (en zone vulnérable sans dérogation) | **Bloquant** : "Attention, chargement excessif pour la zone vulnérable." |
| **PAC (Ecorégime)** | Diversité Assolement | `Nb_Cultures >= 3` | **Alerte** : "Vérifiez la diversité pour l'écorégime niveau 1." |
| **Autonomie Protéique** | Achat Correcteur (T) | `Achat < Seuil_KType` | **Conseil** : "Réduisez le tourteau de soja importé." |
| **Bien-être Animal** | Surface par animal | `Batiment_m2 / UGB >= Norme` | **Info** : "Vérifiez la capacité bâtiment si augmentation troupeau." |

## 5. Structure du Code (Pseudo-code)

```python
class SimulationEngine:
    def __init__(self, farm_data, k_types_db):
        self.farm = farm_data
        self.k_types = k_types_db

    def find_target_ktype(self):
        # Logique de recherche du "meilleur voisin"
        candidates = self.k_types.filter(region=self.farm.region, filiere=self.farm.filiere)
        # On cherche celui avec le meilleur score carbone accessible
        return min(candidates, key=lambda k: distance(self.farm, k) * k.carbon_score)

    def simulate_scenario(self, target_herbe_percent):
        # 1. Appliquer le changement physique
        new_farm_state = self.farm.apply_change(herbe=target_herbe_percent)
        
        # 2. Vérifier Réglementation
        compliance = check_regulations(new_farm_state)
        if not compliance.is_valid:
            return compliance.error_message
            
        # 3. Calculer les nouveaux indicateurs
        results = calculate_indicators(new_farm_state)
        
        return results
```
