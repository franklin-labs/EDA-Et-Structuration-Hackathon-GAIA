import pandas as pd
import json

excel_path = 'base_inosys.xlsx'

def map_filiere_ktypes(file_path):
    print(f"--- Mapping Filieres to K-Types from: {file_path} ---")
    try:
        xls = pd.ExcelFile(file_path, engine='calamine')
        
        # Load Caractéristiques
        df_car = pd.read_excel(xls, sheet_name='Caractéristiques')
        
        # Clean headers
        header_row = df_car.iloc[1].astype(str).tolist()
        header_row_clean = [h.strip() for h in header_row]
        
        # Identify key columns
        nordre_col = header_row_clean.index("NORDRE") if "NORDRE" in header_row_clean else -1
        ktype_col = header_row_clean.index("STRUC.CT_SOUSTITRE") if "STRUC.CT_SOUSTITRE" in header_row_clean else -1
        
        if nordre_col == -1 or ktype_col == -1:
            print("❌ Critical columns (NORDRE or STRUC.CT_SOUSTITRE) missing in Caractéristiques.")
            return

        # Extract NORDRE -> K-Type map
        car_data = df_car.iloc[4:]
        nordre_to_ktype = dict(zip(car_data.iloc[:, nordre_col], car_data.iloc[:, ktype_col]))
        
        filiere_map = {}
        
        # Iterate over Atelier sheets
        for sheet in xls.sheet_names:
            if "Atelier" in sheet:
                filiere_name = sheet.replace("Atelier ", "")
                print(f"\nAnalyzing Filiere: {filiere_name}")
                
                df_at = pd.read_excel(xls, sheet_name=sheet)
                
                at_headers = df_at.iloc[1].astype(str).tolist()
                at_headers_clean = [h.strip() for h in at_headers]
                
                if "NORDRE" in at_headers_clean:
                    at_nordre_col = at_headers_clean.index("NORDRE")
                    
                    # Prepare base data
                    df_data = df_at.iloc[4:]
                    # Drop rows where NORDRE is NaN
                    df_data = df_data.dropna(subset=[df_at.columns[at_nordre_col]])

                    # Define filter column based on filiere
                    filter_col = None
                    if filiere_name == "Bovins lait":
                        filter_col = "FONC1.NBVL" if "FONC1.NBVL" in at_headers_clean else "FONC1.NUGBBL"
                    elif filiere_name == "Bovins viande":
                        filter_col = "FONC1.NBVA" if "FONC1.NBVA" in at_headers_clean else "FONC1.NUGBBV"
                    elif filiere_name == "Ovins lait":
                        filter_col = "FONC1.NBBL" if "FONC1.NBBL" in at_headers_clean else "FONC1.NUGBOL"
                    elif filiere_name == "Ovins viande":
                        filter_col = "FONC1.NBBV" if "FONC1.NBBV" in at_headers_clean else "FONC1.NUGBOV"
                    elif filiere_name == "Caprins":
                        filter_col = "FONC1.NBCH" if "FONC1.NBCH" in at_headers_clean else "FONC1.NUGBCA"
                    elif filiere_name == "Grandes cultures":
                        filter_col = "FONC1.HAGCU"
                    
                    if filter_col and filter_col in at_headers_clean:
                        col_idx = at_headers_clean.index(filter_col)
                        numeric_vals = pd.to_numeric(df_data.iloc[:, col_idx], errors='coerce').fillna(0)
                        valid_mask = numeric_vals > 0
                        
                        df_filtered = df_data[valid_mask]
                        print(f"  Filtered using {filter_col} > 0: {len(df_filtered)} valid rows.")
                        at_nordres = df_filtered.iloc[:, at_nordre_col].unique()
                        
                    elif filiere_name == "Equins":
                        # Special check for Equins
                        if "STRUC.LTATEQ" in at_headers_clean:
                            col_idx = at_headers_clean.index("STRUC.LTATEQ")
                            # Check if not NaN
                            df_filtered = df_data[df_data.iloc[:, col_idx].notna()]
                            print(f"  Filtered using STRUC.LTATEQ not empty: {len(df_filtered)} valid rows.")
                            at_nordres = df_filtered.iloc[:, at_nordre_col].unique()
                        else:
                            print(f"  ⚠️ STRUC.LTATEQ not found for Equins. Using all rows.")
                            at_nordres = df_data.iloc[:, at_nordre_col].unique()
                    else:
                        print(f"  ⚠️ Filter column {filter_col} not found or not defined. Using all rows.")
                        at_nordres = df_data.iloc[:, at_nordre_col].unique()
                    
                    # Find corresponding K-Types
                    ktypes = set()
                    for n in at_nordres:
                        if n in nordre_to_ktype:
                            ktypes.add(nordre_to_ktype[n])
                    
                    filiere_map[filiere_name] = list(ktypes)
                    print(f"  Found {len(ktypes)} K-Types (from {len(at_nordres)} rows).")
                else:
                    print(f"  ❌ NORDRE column not found in {sheet}")
        
        # Save to JSON
        output_file = 'filiere_ktypes_map.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filiere_map, f, indent=4, ensure_ascii=False)
        print(f"Saved mapping to {output_file}")
        
        return filiere_map

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    map_filiere_ktypes(excel_path)
