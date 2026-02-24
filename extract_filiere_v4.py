import pandas as pd
import numpy as np

# Define file paths
excel_path = 'base_inosys.xlsx'

def extract_filiere_info(file_path):
    print(f"--- Extracting Filiere Info from: {file_path} ---")
    try:
        # Load the Excel file with calamine engine
        xls = pd.ExcelFile(file_path, engine='calamine')
        
        target_sheet = 'Caractéristiques'
        print(f"Analyzing '{target_sheet}'...")
        
        df = pd.read_excel(xls, sheet_name=target_sheet)
        
        # We are looking for OTEX or System Type.
        
        # Iterate safely
        found = False
        for r_idx in range(min(20, len(df))):
            row = df.iloc[r_idx]
            for c_idx, val in enumerate(row):
                # Convert to string to avoid TypeError with float/NaN
                val_str = str(val)
                if "OTEX" in val_str or "Filière" in val_str:
                    print(f"FOUND '{val_str}' at Row {r_idx}, Col {c_idx}")
                    found = True
                    # Extract unique values
                    col_data = df.iloc[r_idx+1:, c_idx]
                    unique_vals = col_data.dropna().unique()
                    print(f"Unique values ({len(unique_vals)}):")
                    for u in unique_vals[:50]: # Show first 50
                        print(f"  - {u}")
                    
        if not found:
            print("Not found in Caractéristiques. Checking 'Synthèse'...")
            df_syn = pd.read_excel(xls, sheet_name='Synthèse')
            for r_idx in range(min(20, len(df_syn))):
                row = df_syn.iloc[r_idx]
                for c_idx, val in enumerate(row):
                    val_str = str(val)
                    if "OTEX" in val_str:
                        print(f"FOUND '{val_str}' at Row {r_idx}, Col {c_idx} in Synthèse")
                        col_data = df_syn.iloc[r_idx+1:, c_idx]
                        unique_vals = col_data.dropna().unique()
                        print(f"Unique values ({len(unique_vals)}):")
                        for u in unique_vals[:50]:
                            print(f"  - {u}")
                        return

    except Exception as e:
        print(f"Error analyzing Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_filiere_info(excel_path)
