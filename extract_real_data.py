import pandas as pd

excel_path = 'base_inosys.xlsx'

def extract_ktypes_and_filieres(file_path):
    print(f"--- Extracting K-Types and Filieres from: {file_path} ---")
    try:
        xls = pd.ExcelFile(file_path, engine='calamine')
        
        # 1. Extract K-Types from Caractéristiques
        df_car = pd.read_excel(xls, sheet_name='Caractéristiques')
        
        # Find column index for 'STRUC.F_SYST'
        # It's in the second row (index 1) usually.
        header_row = df_car.iloc[1].astype(str).tolist()
        print(f"Header Row (Full): {header_row}") 
        
        ktype_col_idx = -1
        # Strip whitespace just in case
        header_row_clean = [h.strip() for h in header_row]
        
        if "STRUC.F_SYST" in header_row_clean:
            ktype_col_idx = header_row_clean.index("STRUC.F_SYST")
            print(f"Found 'STRUC.F_SYST' at index {ktype_col_idx}")
        
        # Fallback: Look for "Systeme" or "Type" in headers if code not found
        if ktype_col_idx == -1:
            print("Trying to find 'Système' column by name...")
            header_row_3 = df_car.iloc[3].astype(str).tolist() # Row 4 (headers)
            for i, h in enumerate(header_row_3):
                if "Système" in h or "Systeme" in h:
                    ktype_col_idx = i
                    print(f"Found '{h}' at index {i}")
                    break
        
        ktypes = []

        # Check STRUC.CT_SOUSTITRE as potential K-Type source
        if "STRUC.CT_SOUSTITRE" in header_row_clean:
            sub_col_idx = header_row_clean.index("STRUC.CT_SOUSTITRE")
            subtitles = df_car.iloc[4:, sub_col_idx].dropna().unique().tolist()
            print(f"\nPotential K-Types from STRUC.CT_SOUSTITRE ({len(subtitles)}):")
            for s in subtitles[:10]:
                print(f"  - {s}")
            # Use these as K-Types if F_SYST is missing
            if not ktypes:
                ktypes = subtitles

        # Check STRUC.CT_REFERENCE as another potential source
        if "STRUC.CT_REFERENCE" in header_row_clean:
            ref_col_idx = header_row_clean.index("STRUC.CT_REFERENCE")
            refs = df_car.iloc[4:, ref_col_idx].dropna().unique().tolist()
            print(f"\nPotential K-Types from STRUC.CT_REFERENCE ({len(refs)}):")
            for r in refs[:10]:
                print(f"  - {r}")
        
        # If still no K-Types, check Synthèse sheet
        if not ktypes:
            print("\nChecking 'Synthèse' sheet for K-Types...")
            df_syn = pd.read_excel(xls, sheet_name='Synthèse')
            # Look for headers in first few rows
            for r in range(5):
                row_vals = df_syn.iloc[r].astype(str).tolist()
                if "STRUC.F_SYST" in row_vals:
                    ktype_col_idx = row_vals.index("STRUC.F_SYST")
                    print(f"Found 'STRUC.F_SYST' in Synthèse at Row {r}, Col {ktype_col_idx}")
                    ktypes = df_syn.iloc[r+1:, ktype_col_idx].dropna().unique().tolist()
                    print(f"Found {len(ktypes)} K-Types in Synthèse:")
                    for k in ktypes[:10]:
                        print(f"  - {k}")
                    break
        
        # 2. Identify Filieres from Sheet Names

        # 2. Identify Filieres from Sheet Names
        print("\n✅ Detected Filieres (based on Sheets):")
        filieres = []
        for sheet in xls.sheet_names:
            if "Atelier" in sheet:
                filiere_name = sheet.replace("Atelier ", "")
                filieres.append(filiere_name)
                print(f"  - {filiere_name}")
                
        return ktypes, filieres

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_ktypes_and_filieres(excel_path)
