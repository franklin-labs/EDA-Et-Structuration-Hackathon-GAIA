
import pandas as pd

excel_path = 'base_inosys.xlsx'

def debug_header():
    xls = pd.ExcelFile(excel_path, engine='calamine')
    sheet = 'Atelier Grandes cultures'
    
    print(f"--- Reading {sheet} with header=1 ---")
    df = pd.read_excel(xls, sheet_name=sheet, header=1)
    print("Columns:", df.columns.tolist())
    print("Head:")
    print(df.head())
    
    # Check if we filtered out everything
    df_clean = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    print("Cleaned Columns:", df_clean.columns.tolist())
    print("Cleaned Shape:", df_clean.shape)

if __name__ == "__main__":
    debug_header()
