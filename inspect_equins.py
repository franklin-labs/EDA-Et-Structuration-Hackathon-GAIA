import pandas as pd

excel_path = 'base_inosys.xlsx'

def inspect_equins(file_path):
    try:
        xls = pd.ExcelFile(file_path, engine='calamine')
        df = pd.read_excel(xls, sheet_name='Atelier Equins')
        print(df.columns.tolist())
        print(df.iloc[1].tolist()) # Codes
    except Exception as e:
        print(e)

if __name__ == "__main__":
    inspect_equins(excel_path)
