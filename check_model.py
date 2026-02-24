import joblib
import pandas as pd

try:
    model = joblib.load('model_ktype.pkl')
    print("Modèle chargé avec succès.")
    
    # Vérifier les colonnes attendues
    preprocessor = model.named_steps['preprocessor']
    
    # Pour un ColumnTransformer
    for name, transformer, columns in preprocessor.transformers_:
        if name != 'remainder':
            print(f"Transformer '{name}' attend les colonnes : {columns}")
            
except Exception as e:
    print(f"Erreur lors du chargement : {e}")
