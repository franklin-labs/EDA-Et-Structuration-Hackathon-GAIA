import pandas as pd
excel_path = 'base_inosys.xlsx'

def inspect_columns(sheet_name):
    print(f"\n--- Inspecting {sheet_name} ---")
    try:
        xls = pd.ExcelFile(excel_path, engine='calamine')
        df = pd.read_excel(xls, sheet_name=sheet_name)
        # Row 1 (index 1) usually contains the variable names
        headers = df.iloc[1].astype(str).tolist()
        print(headers)
    except Exception as e:
        print(f"Error reading {sheet_name}: {e}")

inspect_columns('Caractéristiques')
inspect_columns('Système fourrager')
