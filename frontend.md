# Frontend - Interface Conseiller & Simulateur Systémique

Ce document décrit la structure de l'interface utilisateur, conçue pour être utilisée par un conseiller agricole lors de visites ou de sessions de travail.

## 1. Philosophie de l'Interface

L'objectif est de fournir un outil **visuel et pédagogique**. Il ne s'agit pas d'un simple formulaire, mais d'un **tableau de bord interactif** où chaque modification d'un levier (comme la surface en herbe) montre immédiatement son impact sur la trajectoire vers le K-Type cible.

## 2. Structure des Vues

### A. Tableau de Bord (Landing Page)
Vue synthétique de l'activité du conseiller.
*   **KPIs** : Nombre d'agriculteurs accompagnés, Surface totale auditée, Tonnage Carbone évité potentiel.
*   **Liste Clients** : Tableau triable par date de visite, état (En cours, Validé), et alerte réglementaire.
*   **Actions Phares** : Les leviers les plus recommandés (ex: "Augmentation Herbe", "Implantation Méteil").

### B. Simulateur "What-If" (Cœur du Système)
L'outil principal utilisé face à l'agriculteur.

#### Zone 1 : Situation Initiale (Gauche)
*   **Saisie Rapide** : SAU, UGB, Filière (Liste déroulante intelligente).
*   **Jauge K-Type Actuel** : "Vous êtes proche du profil *Laitier Intensif Maïs*".
*   **Indicateurs Clés** : Autonomie (%), Carbone (tCO2e), Marge (€/ha).

#### Zone 2 : Levier d'Action (Centre)
C'est ici que l'utilisateur agit sur la variable principale.
*   **Slider "Surface Herbe"** : Permet de faire varier la part d'herbe de 0% à 100%.
*   **Feedback Immédiat** : Une jauge se déplace en temps réel.
*   **Contraintes Réglementaires** : Des marqueurs rouges sur le slider indiquent les zones à risque (ex: "Zone Vulnérable > 170kg N/ha").

#### Zone 3 : Projection Cible (Droite)
*   **Jauge K-Type Cible** : "Objectif : *Laitier Herbager Autonome*".
*   **Delta** : "Gain Autonomie : +15 pts", "Gain Carbone : -10 tCO2e".
*   **Radar Chart** : Superposition des polygones "Situation Actuelle" vs "Cible K-Type".

### C. Assistant IA (Chat Contextuel)
Une fenêtre de chat toujours accessible.
*   **Rôle** : Répondre aux questions techniques ou réglementaires pointues.
*   **Contexte** : L'IA "sait" quelle ferme est simulée et adapte ses réponses (ex: "Pour cette surface de 80ha, l'aide à la conversion bio serait de...").

## 3. Wireframe (Schéma Conceptuel)

```
+-------------------------------------------------------+
|  [Logo AgriTransition]   Dashboard   Simulateur   IA  |
+-------------------------------------------------------+
|                                                       |
|  [Situation Actuelle]      [Levier Principal]         |
|  Filière: Lait             Surface Herbe: [====O--]   |
|  SAU: 100ha                (60%) -> (75%)             |
|  UGB: 80                   (! Zone Vulnérable)        |
|  -----------------         ------------------         |
|  Profil: Intensif          Action: +15ha Herbe        |
|                                                       |
+-------------------------------------------------------+
|                                                       |
|  [Résultats Comparatifs]                              |
|  Autonomie:  50% -> 70%  (Objectif K-Type: 80%)       |
|  Carbone:    800t -> 750t                             |
|  Marge:      Stabe (Moins d'intrants, moins de lait)  |
|                                                       |
+-------------------------------------------------------+
|  [Chatbot IA]                                         |
|  "Attention, en augmentant la surface herbe,          |
|   vérifiez le chargement instantané au printemps..."  |
+-------------------------------------------------------+
```

## 4. Interactions Clés

1.  **Init** : Le conseiller charge les données (ou saisit).
2.  **Diagnostique** : Le système affiche le K-Type actuel.
3.  **Simule** : Le conseiller bouge le slider "Herbe".
4.  **Alerte** : Si le chargement dépasse 1.7 UGB/ha (Directive Nitrates), une pop-up "Attention Réglementation" apparaît.
5.  **Converge** : Le système indique "Bravo, vous vous rapprochez du K-Type *Herbager Durable*".
