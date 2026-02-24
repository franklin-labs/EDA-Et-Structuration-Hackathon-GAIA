# Frontend - Interface Conseiller & UX Avancée

Ce document décrit la structure de l'interface utilisateur, conçue comme un véritable **Assistant Intelligent (AI-First)** pour le conseiller.

## 1. Philosophie UX : "Perplexity-Like"

L'interface s'inspire des moteurs de réponse modernes. Elle ne se contente pas d'afficher des formulaires, elle **dialogue** et **argumente**.
*   **Sidebar Navigation** : Accès rapide aux contextes (Clients, Outils, Veille).
*   **Split View** : L'écran est divisé entre le **Chat Contextuel** (à gauche ou overlay) et l'**Espace de Travail** (Simulation, Dashboard).
*   **Réponses Sourcées** : Chaque conseil donné par l'IA est justifié par une référence technique (Fiche INOSYS, Règlementation).

## 2. Configuration Ferme & Simulation

L'interface permet de saisir l'ensemble des variables réglementaires et structurelles nécessaires au profilage K-Type :

*   **Structure** : SAU (ha), UMO (Travail), UGB (Cheptel), Nb Vaches Laitières.
*   **Assolement Détaillé** : SFP (Surface Fourragère), Herbe PP (Permanente), Herbe PT (Temporaire), Cultures de vente.

### Simulation "Surface en Herbe"
Un slider interactif permet de simuler une transition vers un système plus herbager. L'interface affiche en temps réel les deltas sur :
*   **Autonomie Fourragère** (%)
*   **Empreinte Carbone** (tCO2)
*   **Biodiversité** (Score 0-10)

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
