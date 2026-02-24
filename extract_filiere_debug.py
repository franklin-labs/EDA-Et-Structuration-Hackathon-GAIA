import pandas as pd
import numpy as np

# Define file paths
excel_path = 'base_inosys.xlsx'

def extract_filiere_info(file_path):
    print(f"--- Extracting Filiere Info from: {file_path} ---")
    try:
        # Load the Excel file with calamine engine
        xls = pd.ExcelFile(file_path, engine='calamine')
        
        # Check all sheets for potential OTEX column
        # "Caractéristiques" was checked but maybe I missed it if "OTEX" is not in the first 20 rows or columns?
        # Actually, let's just dump the columns of "Caractéristiques" to see what we have.
        
        target_sheet = 'Caractéristiques'
        print(f"Inspecting '{target_sheet}' columns...")
        df = pd.read_excel(xls, sheet_name=target_sheet)
        print(df.columns.tolist())
        print(df.iloc[0].tolist()) # Row 1 (codes)
        print(df.iloc[1].tolist()) # Row 2 (labels maybe?)
        print(df.iloc[3].tolist()) # Row 4 (headers?)
        
        # Let's also check "Système fourrager"
        print("\nInspecting 'Système fourrager'...")
        df_sf = pd.read_excel(xls, sheet_name='Système fourrager')
        print(df_sf.columns.tolist())
        print(df_sf.iloc[1].tolist())

        # And "Atelier Bovins lait" just in case
        print("\nInspecting 'Atelier Bovins lait'...")
        df_bl = pd.read_excel(xls, sheet_name='Atelier Bovins lait')
        print(df_bl.iloc[1].tolist())

    except Exception as e:
        print(f"Error analyzing Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_filiere_info(excel_path)
