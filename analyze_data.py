
import pandas as pd
import pdfplumber
import os

# Define file paths
excel_path = 'base_inosys.xlsx'
pdf_path = 'Commande Portail INOSYS 2026-02-23 10h27-46 Dictionnaire PI0001.pdf'

def analyze_excel(file_path):
    print(f"--- Analyzing Excel: {file_path} ---")
    try:
        # Load the Excel file
        xls = pd.ExcelFile(file_path)
        print(f"Sheet names: {xls.sheet_names}")
        
        for sheet_name in xls.sheet_names:
            print(f"\nSheet: {sheet_name}")
            df = pd.read_excel(xls, sheet_name=sheet_name)
            print(f"Shape: {df.shape}")
            print("Columns:", df.columns.tolist())
            print("\nFirst 3 rows:")
            print(df.head(3))
            print("\nData Types:")
            print(df.dtypes)
            print("\nMissing Values:")
            print(df.isnull().sum())
            
            # Identify potential categorical and numerical columns
            print("\nPotential Categorical Columns (unique values < 20):")
            for col in df.columns:
                if df[col].nunique() < 20:
                    print(f"  - {col}: {df[col].unique()}")
                    
    except Exception as e:
        print(f"Error analyzing Excel file: {e}")

def analyze_pdf(file_path):
    print(f"\n--- Analyzing PDF: {file_path} ---")
    try:
        with pdfplumber.open(file_path) as pdf:
            print(f"Number of pages: {len(pdf.pages)}")
            
            # Extract text from the first few pages to understand structure
            print("\n--- Content of Page 1 ---")
            page1 = pdf.pages[0]
            text1 = page1.extract_text()
            print(text1)
            
            if len(pdf.pages) > 1:
                print("\n--- Content of Page 2 ---")
                page2 = pdf.pages[1]
                text2 = page2.extract_text()
                print(text2)
                
            # Try to extract tables if any
            print("\n--- Extracted Tables from Page 1 ---")
            tables = page1.extract_tables()
            for i, table in enumerate(tables):
                print(f"Table {i+1}:")
                for row in table[:3]: # Print first 3 rows of table
                    print(row)
                    
    except Exception as e:
        print(f"Error analyzing PDF file: {e}")

if __name__ == "__main__":
    if os.path.exists(excel_path):
        analyze_excel(excel_path)
    else:
        print(f"File not found: {excel_path}")
        
    if os.path.exists(pdf_path):
        analyze_pdf(pdf_path)
    else:
        print(f"File not found: {pdf_path}")
