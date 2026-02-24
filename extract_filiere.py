import pandas as pd

# Define file paths
excel_path = 'base_inosys.xlsx'

def extract_filiere_info(file_path):
    print(f"--- Extracting Filiere Info from: {file_path} ---")
    try:
        # Load the Excel file with calamine engine
        xls = pd.ExcelFile(file_path, engine='calamine')
        
        # Looking for the sheet that contains General Identification or Filiere info
        # Based on previous analysis, "Identification générale" seems promising
        target_sheet = "Identification générale"
        
        if target_sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=target_sheet)
            
            # The data seems to be transposed or in a specific format (Header in row 1)
            # Row 1 (index 1) seems to contain variable codes like "IDENT.F_OTEX_DE"
            
            # Let's try to find the column for OTEX
            # It seems row 1 contains the headers/codes.
            
            # Let's grab the row with codes (usually row 1, 0-indexed is 1)
            # Actually, let's look at the first few rows again
            print(df.iloc[0:5])
            
            # It seems row 1 (index 1) has the codes.
            # "IDENT.F_OTEX_DE" or similar might be the OTEX code.
            
            # Let's find columns that might contain OTEX info
            # We'll search for "OTEX" in the second row (index 1)
            
            header_row_idx = 1
            headers = df.iloc[header_row_idx].astype(str).tolist()
            
            otex_col_idx = -1
            for i, h in enumerate(headers):
                if "OTEX" in h:
                    print(f"Found OTEX column candidate: {h} at index {i}")
                    otex_col_idx = i
                    break # Assume the first one is the main OTEX
            
            if otex_col_idx != -1:
                # Extract the OTEX column, starting from data row (index 2 onwards)
                otex_series = df.iloc[header_row_idx+1:, otex_col_idx]
                
                print("\n--- Unique OTEX Found ---")
                unique_otex = otex_series.unique()
                for o in unique_otex:
                    print(o)
                    
                # Also try to find "Systeme" or "K-Type" if available
                # Maybe "IDENT.K_TYPE" or similar?
                ktype_col_idx = -1
                for i, h in enumerate(headers):
                    if "TYPE" in h or "SYST" in h:
                         print(f"Found Type/System column candidate: {h} at index {i}")
                
            else:
                print("Could not find OTEX column in header row.")
                
        else:
            print(f"Sheet '{target_sheet}' not found.")

    except Exception as e:
        print(f"Error analyzing Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_filiere_info(excel_path)
