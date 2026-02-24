import pandas as pd
import json
import numpy as np

excel_path = 'base_inosys.xlsx'
output_csv = 'real_farms_dataset.csv'

def extract_real_data():
    print("--- Extracting Real Data from Excel ---")
    try:
        xls = pd.ExcelFile(excel_path, engine='calamine')
        
        # 1. Load Caractéristiques (Base info)
        df_car = pd.read_excel(xls, sheet_name='Caractéristiques')
        # Skip metadata rows (first 4 rows usually, but row 1 is header)
        # Headers are at index 1
        df_car.columns = df_car.iloc[1]
        df_car = df_car.iloc[4:].reset_index(drop=True)
        
        # Select columns
        cols_car = {
            'NORDRE': 'id',
            'STRUC.CT_SOUSTITRE': 'ktype',
            'FONC1.TSAU': 'sau',
            'STRUC.NTRA_NTRAN': 'umo',
            'FONC1.TOTUGB': 'ugb',
            'FONC1.HASFP': 'surface_sfp',
            'FONC1.HAGCU': 'surface_culture',
            'FONC1.HASH': 'surface_herbe_total'
        }
        
        # Keep only existing columns
        existing_cols = [c for c in cols_car.keys() if c in df_car.columns]
        df_base = df_car[existing_cols].rename(columns=cols_car)
        
        # Convert to numeric
        num_cols = ['sau', 'umo', 'ugb', 'surface_sfp', 'surface_culture', 'surface_herbe_total']
        for c in num_cols:
            if c in df_base.columns:
                df_base[c] = pd.to_numeric(df_base[c], errors='coerce').fillna(0)
        
        print(f"Base data loaded: {len(df_base)} rows.")

        # 2. Load Système fourrager (for Herbe PP/PT details)
        if 'Système fourrager' in xls.sheet_names:
            df_sys = pd.read_excel(xls, sheet_name='Système fourrager')
            df_sys.columns = df_sys.iloc[1]
            df_sys = df_sys.iloc[4:].reset_index(drop=True)
            
            if 'NORDRE' in df_sys.columns and 'FONC1.HASTH' in df_sys.columns:
                df_sys_sel = df_sys[['NORDRE', 'FONC1.HASTH']].rename(columns={'NORDRE': 'id', 'FONC1.HASTH': 'surface_herbe_pp'})
                df_sys_sel['surface_herbe_pp'] = pd.to_numeric(df_sys_sel['surface_herbe_pp'], errors='coerce').fillna(0)
                
                # Merge
                df_base = pd.merge(df_base, df_sys_sel, on='id', how='left')
                df_base['surface_herbe_pp'] = df_base['surface_herbe_pp'].fillna(0)
                
                # Calculate PT
                if 'surface_herbe_total' in df_base.columns:
                    df_base['surface_herbe_pt'] = df_base['surface_herbe_total'] - df_base['surface_herbe_pp']
                    df_base['surface_herbe_pt'] = df_base['surface_herbe_pt'].apply(lambda x: max(0, x))
            else:
                print("Warning: FONC1.HASTH not found in Système fourrager")
                df_base['surface_herbe_pp'] = 0
                df_base['surface_herbe_pt'] = df_base.get('surface_herbe_total', 0)
        else:
            df_base['surface_herbe_pp'] = 0
            df_base['surface_herbe_pt'] = 0

        # 3. Load Atelier Bovins lait (for NB VL)
        df_base['nb_vl'] = 0
        if 'Atelier Bovins lait' in xls.sheet_names:
            df_bl = pd.read_excel(xls, sheet_name='Atelier Bovins lait')
            df_bl.columns = df_bl.iloc[1]
            df_bl = df_bl.iloc[4:].reset_index(drop=True)
            
            if 'NORDRE' in df_bl.columns and 'FONC1.NBVL' in df_bl.columns:
                df_bl_sel = df_bl[['NORDRE', 'FONC1.NBVL']].rename(columns={'NORDRE': 'id', 'FONC1.NBVL': 'nb_vl_val'})
                df_bl_sel['nb_vl_val'] = pd.to_numeric(df_bl_sel['nb_vl_val'], errors='coerce').fillna(0)
                
                df_base = pd.merge(df_base, df_bl_sel, on='id', how='left')
                df_base['nb_vl'] = df_base['nb_vl_val'].fillna(0)
                df_base.drop(columns=['nb_vl_val'], inplace=True)
        
        # 4. Identify Filiere using the generated JSON map
        # This is more reliable as it uses the specific filtering logic we established
        try:
            with open('filiere_ktypes_map.json', 'r', encoding='utf-8') as f:
                filiere_map = json.load(f)
            
            # Invert map: K-Type -> Filiere
            # Priority: We want to preserve the first assignment if we iterate in priority order.
            # The JSON keys are likely in insertion order.
            # Let's define explicit priority order to be safe.
            priority_order = [
                'Bovins lait', 'Bovins viande', 'Ovins lait', 'Ovins viande', 'Caprins', 'Equins', 'Grandes cultures'
            ]
            
            ktype_to_filiere = {}
            for filiere in priority_order:
                if filiere in filiere_map:
                    for ktype in filiere_map[filiere]:
                        # Only assign if not already assigned (First one wins)
                        if ktype not in ktype_to_filiere:
                            ktype_to_filiere[ktype] = filiere
            
            # Also add any others not in priority list
            for filiere, ktypes in filiere_map.items():
                if filiere not in priority_order:
                    for ktype in ktypes:
                         if ktype not in ktype_to_filiere:
                            ktype_to_filiere[ktype] = filiere
                            
            print(f"Loaded {len(ktype_to_filiere)} K-Type to Filiere mappings.")
            
            # Apply mapping
            df_base['filiere'] = df_base['ktype'].map(ktype_to_filiere).fillna('Autre')
            
        except Exception as e:
            print(f"Could not load filiere map: {e}. Falling back to sheet scanning (unreliable).")
            # Fallback (original logic removed for brevity/safety)
            df_base['filiere'] = 'Unknown'

        
        # Filter out rows with no K-Type or invalid data

        df_final = df_base.dropna(subset=['ktype'])
        df_final = df_final[df_final['ktype'].astype(str).str.strip() != 'nan']
        
        # Clean up
        final_cols = ['ktype', 'filiere', 'region', 'sau', 'umo', 'ugb', 'nb_vl', 'surface_sfp', 'surface_herbe_pp', 'surface_herbe_pt', 'surface_culture']
        # Fill missing cols with 0
        for c in final_cols:
            if c not in df_final.columns:
                df_final[c] = 0
        
        df_final = df_final[final_cols]
        
        print(f"Extracted {len(df_final)} rows.")
        print(df_final.head())
        print(df_final['filiere'].value_counts())
        
        df_final.to_csv(output_csv, index=False)
        print(f"Saved to {output_csv}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_real_data()
