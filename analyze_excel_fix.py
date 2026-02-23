
import pandas as pd
import pdfplumber
import os
from openpyxl.styles import stylesheet

# Monkey patch for openpyxl error 'biltinId'
original_init = stylesheet.NamedCellStyle.__init__

def _init_with_biltinId(self, fontId=None, fillId=None, borderId=None, numFmtId=None, quotePrefix=None, alignment=None, protection=None, extLst=None, biltinId=None, builtinId=None):
    # Call the original init with the correct arguments if possible, or manually set attributes
    # The issue is usually that the file has 'biltinId' instead of 'builtinId'
    # We map 'biltinId' to 'builtinId'
    actual_builtinId = builtinId if builtinId is not None else biltinId
    
    # We can't easily call original_init because it doesn't expect biltinId. 
    # We have to replicate the init logic or wrap it carefully.
    # Looking at openpyxl source, it assigns these directly.
    
    self.fontId = fontId
    self.fillId = fillId
    self.borderId = borderId
    self.numFmtId = numFmtId
    self.quotePrefix = quotePrefix
    self.alignment = alignment
    self.protection = protection
    self.extLst = extLst
    self.builtinId = actual_builtinId

stylesheet.NamedCellStyle.__init__ = _init_with_biltinId

# Define file paths
excel_path = 'base_inosys.xlsx'

def analyze_excel(file_path):
    print(f"--- Analyzing Excel: {file_path} ---")
    try:
        # Load the Excel file
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        print(f"Sheet names: {xls.sheet_names}")
        
        for sheet_name in xls.sheet_names:
            print(f"\nSheet: {sheet_name}")
            df = pd.read_excel(xls, sheet_name=sheet_name)
            print(f"Shape: {df.shape}")
            print("Columns:", df.columns.tolist())
            print("\nFirst 3 rows:")
            print(df.head(3))
            
            # Identify potential categorical and numerical columns
            print("\nColumn Types:")
            print(df.dtypes)
            
            print("\nStatistics for numerical columns:")
            print(df.describe())
            
    except Exception as e:
        print(f"Error analyzing Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if os.path.exists(excel_path):
        analyze_excel(excel_path)
    else:
        print(f"File not found: {excel_path}")
