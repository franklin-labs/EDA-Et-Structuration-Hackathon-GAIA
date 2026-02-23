# Analyse et Spécifications - Assistant Transition Écologique Agricole

Ce document présente l'analyse des données fournies (Base INOSYS et Dictionnaire) et les spécifications pour le développement d'un assistant intelligent dédié à la transition écologique des agriculteurs.

## 1. Analyse détaillée des données

### Sources de données
- **Fichier Excel (`base_inosys.xlsx`)** : Contient les données réelles de 307 exploitations agricoles (Réseaux d'élevage INOSYS).
- **Dictionnaire PDF (`...Dictionnaire PI0001.pdf`)** : Définit les 810 variables potentielles du système.

### Variables Identifiées et Pertinentes
L'analyse a permis d'identifier plus de 140 variables pertinentes pour la transition écologique, classées en 3 catégories principales.

#### A. Environnement & Durabilité (Focus Transition)
Ces variables sont cruciales pour évaluer l'empreinte écologique et le potentiel de transition.
    *   `DCOMP.NFOUR`, `DCOMP.PFOUR`, `DCOMP.KFOUR` : Bilan azote/phosphore/potasse des fourrages (Entrées).
    *   `SYSFOU.PAUTOFC` : Pourcentage d'autonomie des fourrages conservés.
*   **Pratiques Culturales** :
    *   `FONC1.HASTH` : Surface toujours en herbe (Biodiversité, stockage carbone).
    *   `STRUC.SYSABPA` : Système agro-bio (O/N).
    *   `STRUC.RECOURSSP` : Recours aux surfaces pastorales.

#### B. Économie & Viabilité
Variables permettant de s'assurer que la transition est économiquement soutenable.
*   **Indicateurs de Performance** :
    *   `DTGCUCP.GCU_CALCULE` : Coût de production calculé.
    *   `FONC1.CAPPUGB` / `FONC1.CCORUGB` : Chargement (UGB/ha) - Indicateur clé d'intensité.
    *   `DTBL.PRIXLC`, `DTBL.PRIXCONCBL` : Prix du lait et des concentrés (Volatilité des marchés).
*   **Ventes & Achats** :
    *   `DTGCUCP.GCUCP_VENTEGCU`, `DTBVCP.BVCP_VENTEANI` : Ventes grandes cultures / animaux.

#### C. Production & Structure
Variables décrivant le profil de l'exploitation (Feature Engineering).
*   **Structure** :
    *   `FONC1.HASFP` : Surface Fourragère Principale.
    *   `FONC1.TSAU` : Total Surface Agricole Utile.
    *   `STRUC.PATELIER...` : Présence d'ateliers (Bovins Lait, Viande, Grandes Cultures, etc.).
*   **Cheptel** :
    *   `DCOMP.NVIANDE`, `DCOMP.PVIANDE` : Indicateurs liés à la production de viande.

### Qualité des données
- **Taux de remplissage** : Excellent pour les données structurelles et environnementales globales (>99%). Plus faible pour les données spécifiques aux ateliers (30-40%) car chaque ferme n'a pas tous les ateliers.
- **Types** : Mélange de variables numériques (surfaces, montants) et catégorielles (O/N, Codes région).

---

## 2. Méthodologie de sélection des features

Pour le profilage des éleveurs, nous recommandons une approche en entonnoir :

1.  **Filtrage Métier** : Sélection des variables ayant un impact direct sur les leviers de transition (ex: Autonomie fourragère -> réduction import soja -> baisse empreinte carbone).
2.  **Analyse de Corrélation** : Suppression des variables redondantes (ex: `FONC1.HASFP` et `FONC1.TSAU` peuvent être très corrélées).
3.  **Importance par Modèle (Feature Importance)** : Utilisation d'un modèle type Random Forest pour identifier les variables qui discriminent le mieux les fermes "performantes écologiquement" (si label disponible) ou "rentables".
4.  **Gestion des valeurs manquantes** :
    *   Pour les variables structurelles (Ateliers) : Imputation par 0 ou "Non".
    *   Pour les variables numériques (Prix, Rendements) : Imputation par la médiane régionale ou par système (KNN Imputer).

---

## 3. Algorithme de ML recommandé

### Choix : XGBoost (Gradient Boosting Trees)

**Justification :**
*   **Performance sur données tabulaires** : État de l'art pour ce type de données hétérogènes (mix numérique/catégoriel).
*   **Interprétabilité (SHAP Values)** : Crucial pour les conseillers. On peut expliquer *pourquoi* le modèle recommande une action (ex: "Votre chargement est trop élevé par rapport à votre autonomie fourragère").
*   **Gestion des manquants** : Gère nativement les valeurs manquantes.
*   **Flexibilité** : Peut être utilisé en Régression (prédire le gain carbone) ou en Classification (Recommander "Transition Bio" vs "Optimisation Conventionnelle").

### Configuration
*   **Hyperparamètres clés** : `max_depth` (3-6 pour éviter surapprentissage), `learning_rate` (0.01-0.1), `subsample` (0.8).
*   **Validation** : Validation Croisée (K-Fold, k=5) stratifiée par région ou type de production pour assurer la robustesse.
*   **Métriques** :
    *   *MAE/RMSE* pour les prédictions économiques/environnementales.
    *   *F1-Score* pour la recommandation de scénarios.

---

## 4. Spécifications techniques pour l'application mobile

*   **Architecture** : Modèle hybride "Edge AI" + "Cloud".
    *   *Inférence légère* sur mobile (TFLite / ONNX) pour les simulations rapides hors ligne.
    *   *Entraînement et calculs lourds* sur le Cloud.
*   **Optimisation** :
    *   **Quantization (int8)** : Réduction de la taille du modèle (x4) sans perte majeure de précision.
    *   **Pruning** : Suppression des branches peu utiles des arbres de décision.
*   **Latence cible** : < 200ms pour une recommandation simple.

---

## 5. Architecture de l'agent conversationnel

L'agent agira comme un **Copilote Agricole** utilisant une architecture **RAG (Retrieval-Augmented Generation)**.

### Pipeline NLP
1.  **User Input** : "Comment réduire mes charges d'azote ?"
2.  **Intent Classification (BERT/MobileBERT)** : Détection de l'intention (`OPTIMISATION_CHARGES`, `REGLEMENTATION`, `CONSEIL_TECHNIQUE`).
3.  **Context Retrieval** : Récupération des données de la ferme (Excel) et des fiches techniques (Base de connaissances PDF vectorisée).
4.  **LLM Generation (ex: GPT-4o mini ou Llama-3 fine-tuné)** : Génération de la réponse personnalisée.
    *   *Prompt* : "Tu es un conseiller agricole expert. En te basant sur les données de l'agriculteur (Surface: 150ha, Type: Bovin Lait, Charges Azote: High), donne 3 conseils pratiques."

### Intentions Prédéfinies
*   `DIAGNOSTIC_RAPIDE` : "Quel est mon bilan carbone ?"
*   `SIMULATION_IMPACT` : "Si je passe en bio, quel impact sur ma marge ?"
*   `COMPARAISON` : "Comment je me situe par rapport aux voisins ?"
*   `ALERTE_REGLEMENTAIRE` : "Quelles aides pour la plantation de haies ?"

---

## 6. Fonctionnalités additionnelles

*   **Tableau de bord de suivi** : Visualisation des KPIs (Jauge Carbone, Jauge Marge, Jauge Autonomie).
*   **Alertes Personnalisées** : "Attention, vos charges d'alimentation augmentent plus vite que la moyenne de votre groupe."
*   **Simulateur de Scénarios** : Slider interactif "Réduction cheptel" -> Impact immédiat sur Marge et GES.

---

## 7. Données pour le profil éleveur complet

Pour affiner le modèle, l'application demandera :
1.  **Objectifs** : (ex: "Transmettre ma ferme dans 5 ans", "Maximiser le revenu immédiat", "Réduire le travail d'astreinte").
2.  **Contraintes** : (ex: "Pas d'investissement > 50k€ possible", "Sol très argileux").
3.  **Psychographie** : Appétence au risque, sensibilité écologique.

---

## 8. Critères de succès et KPIs

*   **Taux d'adoption** : % d'agriculteurs actifs mensuellement.
*   **Impact Réel** : Réduction moyenne de GES (tonnes CO2e) chez les utilisateurs vs non-utilisateurs.
*   **Confiance** : Note moyenne de pertinence des conseils (Feedback utilisateur).

---

## 9. Éthique et RGPD

*   **Souveraineté des données** : Les données restent la propriété de l'agriculteur.
*   **Consentement** : Opt-in explicite pour l'utilisation des données à des fins d'entraînement du modèle global.
*   **Anonymisation** : Agrégation des données pour les benchmarks (règle des "min 5 exploitations" pour afficher une moyenne).
*   **Transparence** : L'IA doit être "explicable". Toujours fournir la source du conseil (calcul ou fiche technique).
# EDA-Et-Structuration-Hackathon-GAIA
