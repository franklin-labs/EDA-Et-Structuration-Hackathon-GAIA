# K-Type (Cas-Types) : Méthodologie de Profilage et Benchmarking

## Introduction aux Cas-Types (K-Types)

Dans le contexte des réseaux d'élevage INOSYS, un **Cas-Type (K-Type)** représente un système d'exploitation modélisé, cohérent et optimisé, caractéristique d'une région ou d'un mode de production. Il ne s'agit pas d'une moyenne statistique simple, mais d'une **construction d'experts** validée par le terrain, servant de référence technico-économique.

Pour l'assistant de transition écologique, les K-Types sont utilisés comme **cibles** ou **points de comparaison** pour guider l'agriculteur.

## 1. Identification et Construction des K-Types

Les K-Types sont définis par clustering (regroupement) des exploitations réelles de la base de données (`base_inosys.xlsx`) selon des critères structurels et fonctionnels majeurs.

### Variables discriminantes (Clustering Features)
Pour identifier à quel K-Type appartient une ferme (ou vers lequel elle peut évoluer), nous utilisons les variables suivantes identifiées dans l'analyse :

*   **OTEX (Orientation Technico-Économique)** :
    *   *Bovins Lait* (Spécialisé Plaine, Montagne, Herbager, Maïs...)
    *   *Grandes Cultures* (Céréales, Oléo-protéagineux...)
    *   *Polyculture-Élevage*
*   **Dimension** :
    *   `FONC1.TSAU` (Surface Agricole Utile Totale)
    *   `FONC1.UGB` (Cheptel total)
*   **Intensité / Système Fourrager** :
    *   `FONC1.CHARGEMENT` (UGB/ha SFP)
    *   `SYSFOU.PAUTOFC` (Autonomie fourragère)
    *   `STRUC.MAIS_ENS` (% Maïs dans la SFP)

### Exemple de K-Types (Profils Types)

| Nom du K-Type | Description | Indicateurs Clés (Moyenne) | Objectif Transition |
| :--- | :--- | :--- | :--- |
| **LAIT_HERB_AUTO** | Laitier Herbager Autonome | Chargement < 1.2 UGB/ha, >80% Herbe, Faible Conso Concentrés | Maintien biodiversité, HVE |
| **LAIT_INTENSIF_PLAINE** | Laitier Intensif Plaine | Chargement > 1.8 UGB/ha, >30% Maïs, Haut Rendement Laitier | Réduction Intrants (Azote/Soja), Méthanisation |
| **CULT_BIO_DIV** | Grandes Cultures Bio Diversifiées | Rotation longue (>6 ans), Légumineuses, Pas d'engrais minéral | Optimisation Marge/ha, Carbone Sol |
| **VIANDE_NAISSEUR** | Naisseur Extensif | Chargement < 1.0 UGB/ha, 100% Herbe | Valorisation paysagère, Circuit court |

## 2. Utilisation dans l'Assistant (Le "Gap Analysis")

L'approche K-Type permet de réaliser un **Gap Analysis** (Analyse d'écart) pour l'utilisateur.

### Étape 1 : Classification
L'algorithme classe la ferme actuelle de l'utilisateur dans son K-Type de référence "Actuel" (ex: *Laitier Intensif Plaine*).

### Étape 2 : Projection
L'utilisateur choisit un objectif (ex: "Réduire mon empreinte carbone de 20%"). L'assistant identifie un **K-Type Cible** (ex: *Laitier Herbager Autonome* ou *Laitier Intensif Optimisé*).

### Étape 3 : Recommandation (Le "Chemin de Transition")
Le système calcule les écarts (Gaps) entre la situation actuelle et le K-Type Cible pour générer des actions concrètes.

**Exemple de Gap Analysis :**

*   **Variable** : `SYSFOU.PAUTOFC` (Autonomie Fourragère)
    *   *Actuel* : 65%
    *   *K-Type Cible* : 85%
    *   *Gap* : +20 pts
    *   *Action Recommandée* : "Augmenter la surface en légumineuses de 10ha pour réduire les achats de correcteur azoté."

*   **Variable** : `ECOCSTB.GAZ` (Consommation Gaz)
    *   *Actuel* : 1500 €/an
    *   *K-Type Cible* : 800 €/an
    *   *Gap* : -700 €
    *   *Action Recommandée* : "Installer un pré-refroidisseur de lait et récupérer la chaleur du tank."

## 3. Implémentation Technique

Le module `KTypeMatcher` utilise un algorithme de **K-Nearest Neighbors (KNN)** pondéré :
1.  Il trouve les $k$ fermes les plus proches (voisins) dans la base de données qui ont réussi leur transition (Label "Performance Écologique" élevé).
2.  Il construit un K-Type virtuel (moyenne pondérée de ces voisins performants).
3.  Il restitue ce profil comme objectif atteignable.
