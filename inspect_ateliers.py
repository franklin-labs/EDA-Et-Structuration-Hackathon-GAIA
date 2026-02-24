import pandas as pd
excel_path = 'base_inosys.xlsx'

def inspect_columns(sheet_name):
    print(f"\n--- Inspecting {sheet_name} ---")
    try:
        xls = pd.ExcelFile(excel_path, engine='calamine')
        df = pd.read_excel(xls, sheet_name=sheet_name)
        headers = df.iloc[1].astype(str).tolist()
        # Find columns starting with FONC1 or STRUC
        relevant = [h for h in headers if h.startswith('FONC1') or h.startswith('STRUC')]
        print(f"Relevant columns in {sheet_name}: {relevant}")
    except Exception as e:
        print(f"Error reading {sheet_name}: {e}")

ateliers = [
    'Atelier Bovins lait', 
    'Atelier Bovins viande', 
    'Atelier Ovins lait', 
    'Atelier Ovins viande', 
    'Atelier Caprins',
    'Atelier Equins',
    'Atelier Grandes cultures'
]

for at in ateliers:
    inspect_columns(at)
