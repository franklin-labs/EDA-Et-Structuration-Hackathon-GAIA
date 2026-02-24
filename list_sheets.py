import pandas as pd
excel_path = 'base_inosys.xlsx'
try:
    xls = pd.ExcelFile(excel_path, engine='calamine')
    print("Sheets:", xls.sheet_names)
except Exception as e:
    print(e)
