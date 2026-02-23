
import pandas as pd
import numpy as np
import os

# Define file paths
excel_path = 'base_inosys.xlsx'
dict_path = 'data_dictionary.csv'

def main():
    if not os.path.exists(dict_path):
        print("Dictionary file not found. Run extract_dictionary.py first.")
        return

    # Load dictionary
    try:
        dictionary_df = pd.read_csv(dict_path, index_col=0)
        dictionary = dictionary_df.to_dict(orient='index')
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        return

    print(f"Loaded {len(dictionary)} variables from dictionary.")

    try:
        xls = pd.ExcelFile(excel_path, engine='calamine')
        
        all_features = []
        relevant_features = []
        
        # Define keywords for relevance
        env_keywords = ['gaz', 'carbone', 'énergie', 'azote', 'environnement', 'ges', 'emission', 'biodiversité', 'eau', 'sol']
        eco_keywords = ['marge', 'revenu', 'coût', 'ebc', 'prix', 'vente', 'achat', 'charge']
        prod_keywords = ['surface', 'chargement', 'lait', 'viande', 'culture', 'rendement', 'productivité', 'autonomie']
        
        for sheet_name in xls.sheet_names:
            # Read with header=None to inspect all rows
            try:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            except:
                continue
            
            if df.empty:
                continue
            
            # Find the header row
            header_idx = 2
            
            if header_idx < len(df):
                df.columns = df.iloc[header_idx]
                df = df.iloc[header_idx+1:].reset_index(drop=True)
            else:
                continue
            
            # Clean column names
            df.columns = df.columns.astype(str).str.strip()
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df = df.loc[:, ~df.columns.str.contains('^nan')]
            
            for col in df.columns:
                col_str = str(col)
                
                # Try to find match in dictionary
                desc = "Description not found"
                var_type = "Unknown"
                lookup_key = col_str
                
                if col_str in dictionary:
                    lookup_key = col_str
                else:
                    # Try splitting by dot
                    parts = col_str.split('.')
                    if len(parts) > 1:
                        suffix = parts[-1]
                        if suffix in dictionary:
                            lookup_key = suffix
                
                if lookup_key in dictionary:
                    desc = dictionary[lookup_key].get('description', '')
                    var_type = dictionary[lookup_key].get('type', '')
                
                # Calculate basic stats
                fill_rate = 1 - df[col].isnull().mean()
                unique_vals = df[col].nunique()
                
                # Check relevance
                is_relevant = False
                category = "Other"
                
                desc_lower = str(desc).lower()
                col_lower = col_str.lower()
                
                if any(k in desc_lower or k in col_lower for k in env_keywords):
                    is_relevant = True
                    category = "Environment"
                elif any(k in desc_lower or k in col_lower for k in eco_keywords):
                    is_relevant = True
                    category = "Economic"
                elif any(k in desc_lower or k in col_lower for k in prod_keywords):
                    is_relevant = True
                    category = "Production"
                
                feature_info = {
                    'Sheet': sheet_name,
                    'Variable': col_str,
                    'Description': desc,
                    'Type': var_type,
                    'Fill Rate': fill_rate,
                    'Unique Values': unique_vals,
                    'Category': category,
                    'Is Relevant': is_relevant
                }
                all_features.append(feature_info)
                if is_relevant:
                    relevant_features.append(feature_info)

        # Create DataFrame
        results_df = pd.DataFrame(all_features)
        relevant_df = pd.DataFrame(relevant_features)
        
        # Sort by relevance and fill rate
        if not relevant_df.empty:
            relevant_df = relevant_df.sort_values(by=['Category', 'Fill Rate'], ascending=[True, False])
            relevant_df.to_csv('relevant_features_analysis.csv', index=False)
            
            # Print top features per category
            for cat in ['Environment', 'Economic', 'Production']:
                print(f"\n--- Top {cat} Features (by Fill Rate) ---")
                subset = relevant_df[relevant_df['Category'] == cat].head(10)
                for _, row in subset.iterrows():
                    print(f"{row['Variable']} ({row['Fill Rate']:.1%}): {row['Description']}")
        else:
            print("No relevant features found based on keywords.")

    except Exception as e:
        print(f"Error in main analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
