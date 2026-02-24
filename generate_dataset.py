import pandas as pd
import numpy as np
import random
import json
import os

# Configuration
NUM_SAMPLES = 5000 
REGIONS = ["Bretagne", "Normandie", "Pays de la Loire"]
REAL_DATA_FILE = "real_farms_dataset.csv"

# Load real data if available to estimate distributions
real_stats = {}
try:
    if os.path.exists(REAL_DATA_FILE):
        df_real = pd.read_csv(REAL_DATA_FILE)
        print(f"Loaded real data: {len(df_real)} rows.")
        
        # Group by filiere
        for filiere, group in df_real.groupby('filiere'):
            stats = {}
            for col in ['sau', 'umo', 'ugb', 'nb_vl', 'surface_sfp', 'surface_herbe_pp', 'surface_herbe_pt', 'surface_culture']:
                mean = group[col].mean()
                std = group[col].std()
                if pd.isna(std) or std == 0:
                    std = mean * 0.2 if mean > 0 else 1.0 # Default variation
                stats[col] = (mean, std)
            
            # Also get list of K-Types for this filiere
            ktypes = group['ktype'].dropna().unique().tolist()
            stats['ktypes'] = ktypes
            real_stats[filiere] = stats
            
        print(f"Computed stats for {len(real_stats)} filieres.")
        
except Exception as e:
    print(f"Error analyzing real data: {e}")

# Load filiere to K-Type mapping (fallback/supplement)
try:
    with open('filiere_ktypes_map.json', 'r', encoding='utf-8') as f:
        FILIERE_MAP = json.load(f)
except Exception as e:
    FILIERE_MAP = {}

def generate_farm(id):
    # 1. Select Filiere
    if real_stats:
        # Weighted choice based on real data counts? Or uniform?
        # Let's use uniform to ensure we generate enough samples for rare filieres
        filiere = np.random.choice(list(real_stats.keys()))
        stats = real_stats[filiere]
        
        # Select K-Type from real data if available, else from map
        possible_ktypes = stats.get('ktypes', [])
        if not possible_ktypes and filiere in FILIERE_MAP:
             possible_ktypes = FILIERE_MAP[filiere]
        
        if not possible_ktypes:
             ktype = "Standard"
        else:
             ktype = np.random.choice(possible_ktypes)
             
        # Generate features based on real stats
        farm_data = {}
        for col in ['sau', 'umo', 'ugb', 'nb_vl', 'surface_sfp', 'surface_herbe_pp', 'surface_herbe_pt', 'surface_culture']:
            mean, std = stats.get(col, (0, 1))
            val = np.random.normal(mean, std)
            farm_data[col] = max(0, val) # Ensure non-negative
            
    else:
        # Fallback to hardcoded logic if no real data
        filiere_keys = list(FILIERE_MAP.keys()) if FILIERE_MAP else ["Bovins lait", "Grandes cultures"]
        filiere = np.random.choice(filiere_keys)
        possible_ktypes = FILIERE_MAP.get(filiere, ["Standard"])
        ktype = np.random.choice(possible_ktypes) if possible_ktypes else "Standard"
        
        # Simple fallback generation
        sau = np.random.normal(50, 20)
        farm_data = {
            'sau': max(5, sau),
            'umo': max(1, np.random.normal(1.5, 0.5)),
            'ugb': max(0, np.random.normal(30, 20)),
            'nb_vl': 0,
            'surface_sfp': max(0, sau * 0.8),
            'surface_culture': max(0, sau * 0.2),
            'surface_herbe_pp': max(0, sau * 0.4),
            'surface_herbe_pt': max(0, sau * 0.4)
        }

    # Common fields
    region = np.random.choice(REGIONS)
    
    # Enforce logical constraints
    # SAU >= SFP + Culture
    # We prioritize SFP and Culture based on their generated ratio relative to SAU
    gen_sfp = farm_data['surface_sfp']
    gen_culture = farm_data['surface_culture']
    gen_sau = farm_data['sau']
    
    # If sum > SAU, scale down
    if gen_sfp + gen_culture > gen_sau:
        factor = gen_sau / (gen_sfp + gen_culture) if (gen_sfp + gen_culture) > 0 else 0
        farm_data['surface_sfp'] *= factor
        farm_data['surface_culture'] *= factor
    
    # SFP >= Herbe PP + Herbe PT
    gen_pp = farm_data['surface_herbe_pp']
    gen_pt = farm_data['surface_herbe_pt']
    if gen_pp + gen_pt > farm_data['surface_sfp']:
         factor = farm_data['surface_sfp'] / (gen_pp + gen_pt) if (gen_pp + gen_pt) > 0 else 0
         farm_data['surface_herbe_pp'] *= factor
         farm_data['surface_herbe_pt'] *= factor

    # Rounding
    result = {
        "id": id,
        "region": region,
        "filiere": filiere,
        "ktype": ktype
    }
    for k, v in farm_data.items():
        result[k] = round(v, 1)
        if k == 'nb_vl':
            result[k] = int(v)
            
    return result

print("Generating synthetic dataset (Augmented from Real Data)...")
data = [generate_farm(i) for i in range(NUM_SAMPLES)]
df = pd.DataFrame(data)

# Save
output_csv = "farms_dataset.csv"
df.to_csv(output_csv, index=False)
print(f"Generated {NUM_SAMPLES} farms in '{output_csv}'")
print("\nDistribution of Filieres:")
print(df["filiere"].value_counts())
