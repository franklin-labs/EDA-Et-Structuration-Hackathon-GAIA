import pandas as pd
import numpy as np

# Define file paths
excel_path = 'base_inosys.xlsx'

def extract_filiere_info(file_path):
    print(f"--- Extracting Filiere Info from: {file_path} ---")
    try:
        # Load the Excel file with calamine engine
        xls = pd.ExcelFile(file_path, engine='calamine')
        
        # Based on logs, the sheets seem to be named "Détails atelier ..."
        # Let's inspect "Détails atelier Grandes cultures", "Détails atelier Caprins", "Détails atelier Equins"
        # and see if we can find a main sheet with general info.
        
        # The logs showed "Identification générale" was NOT found in the previous run.
        # Let's list all sheet names first to be sure.
        print(f"All Sheet Names: {xls.sheet_names}")
        
        # We need to find where the "OTEX" or "Filière" information is stored.
        # Usually it's in a summary sheet.
        # Let's check "Identification générale" again, maybe I missed a typo or it has a different name.
        # Or maybe it's "Structure" or similar.
        
        possible_sheets = [s for s in xls.sheet_names if "Ident" in s or "Général" in s or "Structure" in s or "Exploitation" in s]
        print(f"Possible Main Sheets: {possible_sheets}")
        
        if not possible_sheets:
            # Fallback: check all sheets for a column named "OTEX" in the first few rows
            print("No obvious main sheet found. Scanning all sheets for 'OTEX' keyword...")
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, nrows=10, header=None)
                # Convert to string and search
                for r_idx, row in df.iterrows():
                    row_str = row.astype(str).tolist()
                    for c_idx, val in enumerate(row_str):
                        if "OTEX" in val or "Filière" in val or "Production" in val:
                            print(f"Found keyword '{val}' in Sheet '{sheet_name}' at Row {r_idx}, Col {c_idx}")
                            
                            # If found, let's try to extract unique values from this column
                            # Reload the sheet properly
                            full_df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                            # Assuming data starts after the header row
                            data_col = full_df.iloc[r_idx+1:, c_idx]
                            unique_vals = data_col.dropna().unique()
                            print(f"Unique values in '{val}' column (first 20): {unique_vals[:20]}")
                            
        else:
             for sheet_name in possible_sheets:
                print(f"Analyzing potential main sheet: {sheet_name}")
                df = pd.read_excel(xls, sheet_name=sheet_name)
                print(df.head())

    except Exception as e:
        print(f"Error analyzing Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_filiere_info(excel_path)
