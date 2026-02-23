# Frontend - Interface Conseiller & UX Avancée

Ce document décrit la structure de l'interface utilisateur, conçue comme un véritable **Assistant Intelligent (AI-First)** pour le conseiller.

## 1. Philosophie UX : "Perplexity-Like"

L'interface s'inspire des moteurs de réponse modernes. Elle ne se contente pas d'afficher des formulaires, elle **dialogue** et **argumente**.
*   **Sidebar Navigation** : Accès rapide aux contextes (Clients, Outils, Veille).
*   **Split View** : L'écran est divisé entre le **Chat Contextuel** (à gauche ou overlay) et l'**Espace de Travail** (Simulation, Dashboard).
*   **Réponses Sourcées** : Chaque conseil donné par l'IA est justifié par une référence technique (Fiche INOSYS, Règlementation).

## 2. Configuration Ferme (Entrées)

Le formulaire de configuration permet au conseiller de saisir les données structurelles de l'exploitation pour initialiser le profilage K-Type.

### Champs Requis :
*   **Structure & Main d'Œuvre**
    *   **Filière** : Orientation technico-économique (ex: Bovins Lait, Grandes Cultures).
    *   **SAU (ha)** : Surface Agricole Utile totale.
    *   **UMO** : Unités Main d'Œuvre (Total travail sur la ferme).
    *   **UGB Totaux** : Chargement animal total.
    *   **Nb Vaches Laitières (VL)** : Taille du troupeau laitier.

*   **Assolement Détaillé (ha)**
    *   **SFP** : Surface Fourragère Principale.
    *   **Herbe (PP)** : Surface en Prairies Permanentes.
    *   **Herbe (PT)** : Surface en Prairies Temporaires.
    *   **Cultures Vente** : Surface en cultures (Céréales, etc.).

Ces données permettent de calculer automatiquement :
*   Le chargement (UGB/SFP)
*   La part d'herbe dans la SFP (%)
*   La productivité du travail (UGB/UMO ou Lait/UMO)

Ces indicateurs sont ensuite utilisés par le backend pour identifier le **K-Type** de référence.

## 3. Interface de Simulation

```
+----------------+---------------------------------------------------+
| [Sidebar]      |  [Barre de Recherche / Chat Prompt]               |
|                |  "Comment améliorer l'autonomie protéique ?"      |
|  Dashboard     |---------------------------------------------------|
|  Clients       |  [Chat Response Area]        |  [Workspace Area]  |
|  Simulateur    |                              |                    |
|  Docs          |  > Analyse en cours...       |  [Graphique Radar] |
|                |  > D'après la fiche #42:     |   Autonomie: +12%  |
|  [User Profil] |    Le méteil est efficace.   |   Carbone: -5%     |
|                |    [Source: Arvalis]         |                    |
|                |                              |  [Slider Herbe]    |
|                |  > Action:                   |  O-------------    |
|                |  [Simuler Méteil]            |                    |
+----------------+------------------------------+--------------------+
```

## 4. Interactions Avancées

1.  **Drill-Down** : Cliquer sur une source dans le chat ouvre le document dans l'espace de travail.
2.  **Context-Aware** : Si le simulateur est ouvert sur la "Ferme des Lilas", le chat répond spécifiquement pour cette ferme (prise en compte de la SAU, du sol, etc.).
3.  **Export Automatique** : À la fin de la session, le chat peut générer un compte-rendu PDF résumant les simulations et les conseils donnés.
