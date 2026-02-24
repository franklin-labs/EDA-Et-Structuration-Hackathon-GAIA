# %% [markdown]
# # Pipeline d'Entraînement de Modèle K-Type
# 
# Ce notebook (script) implémente un pipeline complet de Machine Learning pour la classification des fermes en Cas-Types (K-Types).
# Il couvre :
# 1.  Chargement et Préparation des données
# 2.  Analyse Non Supervisée (Clustering K-Means) pour valider la structure des données
# 3.  Apprentissage Supervisé (Random Forest vs XGBoost)
# 4.  Optimisation des Hyperparamètres (GridSearch)
# 5.  Export du meilleur modèle

# %%
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# %% [markdown]
# ## 1. Chargement et Préparation des Données

# %%
# Chargement du dataset synthétique
df = pd.read_csv("farms_dataset.csv")
print(f"Dataset chargé : {df.shape[0]} lignes, {df.shape[1]} colonnes")

# Nettoyage des données
df = df.dropna(subset=['ktype'])
print(f"Après suppression des NaNs K-Type : {df.shape[0]} lignes")

# Filtrage des classes trop rares pour la validation croisée
ktype_counts = df['ktype'].value_counts()
valid_ktypes = ktype_counts[ktype_counts >= 5].index
df = df[df['ktype'].isin(valid_ktypes)]
print(f"Après filtrage des K-Types rares (<5 samples) : {df.shape[0]} lignes, {len(valid_ktypes)} classes restantes")

print(df.head())

# Séparation Features (X) et Target (y)
target_col = "ktype"
features_num = ["sau", "umo", "ugb", "nb_vl", "surface_sfp", "surface_herbe_pp", "surface_herbe_pt", "surface_culture"]
features_cat = ["region", "filiere"]

X = df[features_num + features_cat]
y = df[target_col]

# %% [markdown]
# ## 2. Analyse Non Supervisée (Clustering)
# Objectif : Vérifier si des groupes naturels émergent des données sans utiliser les étiquettes K-Type.
# Cela permet de valider la pertinence de nos segments.

# %%
# Preprocessing pour le clustering (uniquement numérique pour simplifier ici)
scaler_clust = StandardScaler()
X_clust = scaler_clust.fit_transform(df[features_num])

# K-Means avec k=7 (approx nombre de filières)
kmeans = KMeans(n_clusters=7, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_clust)

# Ajout des clusters au dataframe pour analyse
df["cluster"] = clusters

# Visualisation (Croisement Cluster vs Vrai K-Type)
crosstab = pd.crosstab(df["cluster"], df["ktype"])
print("\n--- Correspondance Clusters (Non Supervisé) vs K-Types (Supervisé) ---")
print(crosstab)
# Si la diagonale (ou des blocs) est forte, cela valide notre segmentation.

# %% [markdown]
# ## 3. Apprentissage Supervisé & Optimisation
# Nous allons tester plusieurs modèles et optimiser leurs hyperparamètres.

# %%
# Préparation du Pipeline de Preprocessing
# - Variables numériques : Standardisation (Centrer-Réduire)
# - Variables catégorielles : OneHotEncoding
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), features_num),
        ('cat', OneHotEncoder(handle_unknown='ignore'), features_cat)
    ])

# Split Train/Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Définition des modèles à tester
model_pipelines = {
    'RandomForest': Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42, n_jobs=1))
    ]),
    'GradientBoosting': Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', GradientBoostingClassifier(random_state=42))
    ])
}

# Grilles d'hyperparamètres simplifiées pour rapidité
param_grids = {
    'RandomForest': {
        'classifier__n_estimators': [100, 200],
        'classifier__max_depth': [None, 15]
    },
    'GradientBoosting': {
        'classifier__n_estimators': [100],
        'classifier__learning_rate': [0.1],
        'classifier__max_depth': [3, 5]
    }
}

# %% [markdown]
# ## 4. Entraînement et Sélection du Meilleur Modèle

# %%
best_model = None
best_score = 0
best_name = ""

results = {}

print("\n--- Début de l'optimisation (GridSearch) ---")

for name, pipeline in model_pipelines.items():
    print(f"Optimisation de {name}...")
    # n_jobs=1 pour éviter les problèmes d'interruption en environnement restreint
    grid_search = GridSearchCV(pipeline, param_grids[name], cv=3, n_jobs=1, verbose=2)
    grid_search.fit(X_train, y_train)
    
    score = grid_search.best_score_
    print(f"  > Meilleur Score CV : {score:.4f}")
    print(f"  > Meilleurs Params : {grid_search.best_params_}")
    
    results[name] = grid_search
    
    if score > best_score:
        best_score = score
        best_model = grid_search.best_estimator_
        best_name = name

print(f"\n🏆 MEILLEUR MODÈLE : {best_name} avec une précision CV de {best_score:.4f}")

# %% [markdown]
# ## 5. Évaluation Finale sur le Test Set

# %%
y_pred = best_model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print("\n--- Rapport de Classification sur Test Set ---")
print(f"Précision Globale : {acc:.4f}")
print(classification_report(y_test, y_pred))

# %% [markdown]
# ## 6. Sauvegarde du Modèle
# Le pipeline complet (Preprocessing + Modèle optimisé) est sauvegardé.

# %%
joblib.dump(best_model, "model_ktype.pkl")
print("\n✅ Modèle sauvegardé sous 'model_ktype.pkl'")

# Test de rechargement rapide
loaded_model = joblib.load("model_ktype.pkl")
sample = X_test.iloc[0:1]
print("\nTest de prédiction sur un exemple :")
print(sample)
print(f"Prédiction : {loaded_model.predict(sample)[0]}")
