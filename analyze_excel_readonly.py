
import pandas as pd

# Define file paths
excel_path = 'base_inosys.xlsx'

def analyze_excel(file_path):
    print(f"--- Analyzing Excel: {file_path} ---")
    try:
        # Load the Excel file with read_only=True to potentially skip some style parsing
        xls = pd.ExcelFile(file_path, engine='openpyxl', engine_kwargs={'read_only': True})
        print(f"Sheet names: {xls.sheet_names}")
        
        for sheet_name in xls.sheet_names:
            print(f"\nSheet: {sheet_name}")
            # read_only mode doesn't support reading by name easily if not iterated, but pandas handles it.
            df = pd.read_excel(xls, sheet_name=sheet_name)
            print(f"Shape: {df.shape}")
            print("Columns:", df.columns.tolist())
            print("\nFirst 3 rows:")
            print(df.head(3))
            
            # Identify potential categorical and numerical columns
            print("\nColumn Types:")
            print(df.dtypes)
            
            # Only describe if we have data
            if not df.empty:
                print("\nStatistics for numerical columns:")
                print(df.describe())
            
    except Exception as e:
        print(f"Error analyzing Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_excel(excel_path)
