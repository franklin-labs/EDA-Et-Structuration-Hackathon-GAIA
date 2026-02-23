
import pandas as pd
import openpyxl.styles.stylesheet as ss

# Monkey patch CellStyle
original_init = ss.CellStyle.__init__

def patched_init(self, numFmtId=None, fontId=None, fillId=None, borderId=None, xfId=None, quotePrefix=None, alignment=None, protection=None, extLst=None, builtinId=None, name=None, hidden=None, iLevel=None, biltinId=None):
    # Handle biltinId typo
    actual_builtinId = builtinId if builtinId is not None else biltinId
    
    # Call original init without biltinId
    # Since original_init likely doesn't accept **kwargs, we need to be careful.
    # But wait, original_init is what's failing because it doesn't accept biltinId.
    # So we must NOT call original_init with biltinId.
    
    # We can try to reconstruct the object manually or call the original one with the correct arguments.
    # Looking at openpyxl source code for CellStyle:
    # def __init__(self, numFmtId=None, fontId=None, fillId=None, borderId=None, xfId=None, quotePrefix=None, alignment=None, protection=None, extLst=None, builtinId=None, name=None, hidden=None, iLevel=None):
    
    self.numFmtId = numFmtId
    self.fontId = fontId
    self.fillId = fillId
    self.borderId = borderId
    self.xfId = xfId
    self.quotePrefix = quotePrefix
    self.alignment = alignment
    self.protection = protection
    self.extLst = extLst
    self.builtinId = actual_builtinId
    self.name = name
    self.hidden = hidden
    self.iLevel = iLevel

ss.CellStyle.__init__ = patched_init

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
    analyze_excel(excel_path)
