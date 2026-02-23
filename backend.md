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

## 2. Algorithme de Profilage (K-Type Matching)

Le backend maintient un "State" de la session courante.
*   Si le conseiller modifie `part_herbe` via le slider, le backend met à jour le contexte du chat.
*   Le Chatbot peut alors commenter proactivement : *"Attention, avec 70% d'herbe, vérifiez votre capacité de stockage fourrager."*

## 3. Endpoints Clés

| Endpoint | Méthode | Description |
| :--- | :--- | :--- |
| `/chat/stream` | POST | Chat temps réel (SSE) avec étapes de raisonnement. |
| `/context/update` | POST | Met à jour l'état de la ferme simulée (ex: après modif slider). |
| `/docs/{id}` | GET | Récupère le contenu d'une source citée. |
| `/advisor/stats` | GET | Données agrégées pour le Dashboard (inchangé). |

## 4. Sécurité & Rôles
*   **Authentification** : Token JWT Conseiller.
*   **Accès** : Le conseiller ne voit que ses fermes (Row-Level Security).
