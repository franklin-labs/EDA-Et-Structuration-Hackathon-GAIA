# K-Type (Cas-Types) : Méthodologie de Profilage et Simulation Systémique

## Introduction aux Cas-Types (K-Types)

Dans le contexte des réseaux d'élevage INOSYS, un **Cas-Type (K-Type)** représente un système d'exploitation modélisé, cohérent et optimisé, caractéristique d'une région ou d'un mode de production. Il ne s'agit pas d'une moyenne statistique simple, mais d'une **construction d'experts** validée par le terrain, servant de référence technico-économique.

Pour l'assistant de transition écologique, les K-Types sont utilisés pour **simuler le comportement global du système** lorsqu'on modifie une variable clé.

## 1. Identification et Construction des K-Types

Les K-Types sont définis par clustering (regroupement) des exploitations réelles de la base de données (`base_inosys.xlsx`) selon des critères structurels et fonctionnels majeurs.

### Variables discriminantes (Clustering Features)
Pour identifier à quel K-Type appartient une ferme, nous utilisons les variables suivantes :

*   **FILIÈRE** :
    *   *Bovins Lait* (Spécialisé Plaine, Montagne, Herbager, Maïs...)
    *   *Grandes Cultures* (Céréales, Oléo-protéagineux...)
    *   *Polyculture-Élevage*
*   **Dimension** :
    *   `FONC1.TSAU` (Surface Agricole Utile Totale)
    *   `FONC1.UGB` (Cheptel total)
*   **Intensité / Système Fourrager** :
    *   `FONC1.CHARGEMENT` (UGB/ha SFP)
    *   `STRUC.PART_HERBE` (Pourcentage d'herbe dans la SFP)

### Exemple de K-Types (Profils Types)

| Nom du K-Type | Description | Indicateurs Clés (Moyenne) | Objectif Transition |
| :--- | :--- | :--- | :--- |
| **LAIT_HERB_AUTO** | Laitier Herbager Autonome | Chargement < 1.2 UGB/ha, >80% Herbe | Maintien biodiversité, HVE |
| **LAIT_INTENSIF_PLAINE** | Laitier Intensif Plaine | Chargement > 1.8 UGB/ha, >30% Maïs | Réduction Intrants, Méthanisation |
| **CULT_BIO_DIV** | Grandes Cultures Bio Diversifiées | Rotation longue, Légumineuses | Optimisation Marge/ha, Carbone Sol |
| **VIANDE_NAISSEUR** | Naisseur Extensif | Chargement < 1.0 UGB/ha, 100% Herbe | Valorisation paysagère |

## 2. Simulation Systémique (Approche "What-If")

Au lieu de simplement comparer des moyennes, l'approche K-Type permet de **simuler l'impact systémique** d'un changement.

### Le Principe : "Changer une variable, observer le système"
L'utilisateur définit sa situation actuelle, puis modifie une variable levier (ex: *Augmenter la part d'herbe de 50% à 70%*).

L'agent utilise les règles du K-Type pour prédire les effets en cascade :

1.  **Variable modifiée** : Part d'Herbe (+20%)
2.  **Impact Direct** :
    *   Baisse des surfaces en maïs (-20%)
    *   Baisse des achats d'engrais azotés (Moins de cultures exigeantes)
3.  **Impact Systémique (Calculé)** :
    *   **Autonomie Fourragère** : Augmente (car l'herbe est produite sur place et nécessite moins de correcteur azoté que le maïs).
    *   **Carbone** : Diminue (Stockage carbone sous prairie + Moins d'émissions liées aux engrais).
    *   **Économie** : Baisse du coût alimentaire (Index Coût).

### Exemple de Simulation

*   **Scénario** : Passage d'un système "Maïs Dominant" à "Herbager".
*   **Action** : Slider "Part d'Herbe" déplacé de 30% à 60%.
*   **Réponse de l'Agent** :
    > "En augmentant votre surface en herbe à 60%, votre **autonomie fourragère** passerait de 55% à **72%**.
    > Cela réduirait vos émissions de **15 tonnes CO2e/an** grâce au stockage carbone additionnel.
    > *Attention* : Avec un chargement inchangé, vous devrez peut-être acheter du foin en hiver ou réduire légèrement le cheptel."

## 3. Implémentation Technique

Le module de simulation ne se contente pas d'une règle de trois. Il utilise des courbes de réponse non-linéaires basées sur les données INOSYS :
*   $Autonomie = f(Part\_Herbe, Chargement)$
*   $Carbone = f(Intrants, Stockage\_Sol)$
