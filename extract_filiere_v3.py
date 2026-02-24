import pandas as pd
import numpy as np

# Define file paths
excel_path = 'base_inosys.xlsx'

def extract_filiere_info(file_path):
    print(f"--- Extracting Filiere Info from: {file_path} ---")
    try:
        # Load the Excel file with calamine engine
        xls = pd.ExcelFile(file_path, engine='calamine')
        
        # Based on sheet names: ['Synthèse', 'Liste dossiers Excel', 'Caractéristiques', 'Système fourrager', 'Résultats économiques', 'Environnement', 'Atelier Bovins lait', ...]
        # 'Caractéristiques' seems to be the place for general structure.
        
        target_sheet = 'Caractéristiques'
        print(f"Analyzing '{target_sheet}'...")
        
        df = pd.read_excel(xls, sheet_name=target_sheet)
        
        # Print first few rows to understand structure
        print(df.head(10))
        
        # We are looking for OTEX or System Type.
        # It might be in the first row (header codes) or second row.
        
        # Let's search for "OTEX" in the entire dataframe (first 20 rows)
        for r_idx in range(min(20, len(df))):
            row = df.iloc[r_idx].astype(str)
            for c_idx, val in enumerate(row):
                if "OTEX" in val:
                    print(f"FOUND 'OTEX' at Row {r_idx}, Col {c_idx}: {val}")
                    # Extract unique values from this column starting below the header
                    col_data = df.iloc[r_idx+1:, c_idx]
                    unique_vals = col_data.dropna().unique()
                    print(f"Unique OTEX values found ({len(unique_vals)}):")
                    for u in unique_vals:
                        print(f"  - {u}")
                    return # Found it, stop searching

        print("OTEX not found in first 20 rows of 'Caractéristiques'. Checking 'Synthèse'...")
        
        df_syn = pd.read_excel(xls, sheet_name='Synthèse')
        for r_idx in range(min(20, len(df_syn))):
            row = df_syn.iloc[r_idx].astype(str)
            for c_idx, val in enumerate(row):
                if "OTEX" in val:
                    print(f"FOUND 'OTEX' at Row {r_idx}, Col {c_idx} in Synthèse: {val}")
                    col_data = df_syn.iloc[r_idx+1:, c_idx]
                    unique_vals = col_data.dropna().unique()
                    print(f"Unique OTEX values found ({len(unique_vals)}):")
                    for u in unique_vals:
                        print(f"  - {u}")
                    return

    except Exception as e:
        print(f"Error analyzing Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_filiere_info(excel_path)
