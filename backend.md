# Backend - Architecture Chat & Support Décisionnel

Ce document décrit l'architecture backend nécessaire pour supporter l'interface "Perplexity-like" du Portail Conseiller.

## 1. Modèle de Données (FarmInput)

L'API attend un objet JSON structuré représentant l'état initial de l'exploitation. Ce modèle est strict pour garantir la qualité du profilage K-Type.

### Champs Obligatoires
*   `region` (string) : Zone géographique (ex: "Bretagne").
*   `filiere` (string) : Orientation principale (ex: "Bovins Lait").
*   `sau` (float) : Surface Agricole Utile (ha).
*   `umo` (float) : Unités Main d'Œuvre (Total).
*   `ugb` (float) : Unités Gros Bétail (Total).
*   `nb_vl` (int) : Nombre de vaches laitières (si applicable).

### Assolement Détaillé
*   `surface_sfp` (float) : Surface Fourragère Principale (ha).
*   `surface_herbe_pp` (float) : Surface Prairies Permanentes (ha).
*   `surface_herbe_pt` (float) : Surface Prairies Temporaires (ha).
*   `surface_culture` (float) : Surface Cultures de Vente (ha).

Ces données permettent de calculer :
*   `chargement` = UGB / SFP
*   `part_herbe` = (Herbe PP + Herbe PT) / SFP

## 2. Intelligence Artificielle & Profilage (K-Type Matching)

Le backend utilise un modèle de **Machine Learning (Random Forest)** entraîné sur 5000 exploitations synthétiques (générées à partir de statistiques réelles INOSYS).

*   **Modèle** : `model_ktype.pkl` (Pipeline Scikit-Learn avec StandardScaler et OneHotEncoder).
*   **Features** : SAU, UMO, UGB, Nb VL, SFP, Herbe PP, Herbe PT, Cultures, Région, Filière.
*   **Précision** : Le modèle identifie dynamiquement le K-Type le plus proche du référentiel de production.

## 3. Endpoints API (FastAPI)

| Endpoint | Méthode | Description |
| :--- | :--- | :--- |
| `/simulate` | POST | Calcule les indicateurs (Autonomie, Carbone, Bio) et prédit le K-Type via ML. |
| `/chat` | POST | Assistant expert "Perplexity-style" avec raisonnement et citations contextuelles. |
| `/advisor/stats` | GET | Statistiques globales pour le tableau de bord du conseiller. |

## 4. Assistant Intelligent (Chat)

Le chatbot (`/chat`) est conçu pour être **Context-Aware** :
*   **Raisonnement** : Chaque réponse inclut les étapes logiques (`reasoning_steps`).
*   **Citations** : Références directes aux fiches techniques INOSYS ou à la réglementation.
*   **Actions Suggérées** : Propose des boutons cliquables pour approfondir l'analyse.
