
import pdfplumber
import pandas as pd
import re

pdf_path = 'Commande Portail INOSYS 2026-02-23 10h27-46 Dictionnaire PI0001.pdf'

def extract_dictionary(pdf_path):
    variable_dict = {}
    pattern = re.compile(r'^\d+\s+\w+\s+(\S+)\s+(.+)\s+(STR|NUM|DATE|O\/N|INT|DEC)')
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Processing {len(pdf.pages)} pages...")
        for i, page in enumerate(pdf.pages):
            if i == 0: continue # Skip summary page
            
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            for line in lines:
                match = pattern.match(line)
                if match:
                    var_name = match.group(1)
                    description = match.group(2).strip()
                    var_type = match.group(3)
                    
                    # Clean up description if it ends with numbers or codes
                    # Sometimes description includes the format if regex matched greedily? No, format is separate group.
                    
                    variable_dict[var_name] = {'description': description, 'type': var_type}
                else:
                    # Sometimes format is missing or line is wrapped?
                    # Let's try simpler split logic for robustness
                    parts = line.split()
                    if len(parts) >= 4 and parts[0].isdigit() and parts[1].isupper():
                        # Heuristic fallback
                        var_name = parts[2]
                        # Assume description is the rest until a known format or end of line
                        # This is risky but catches lines missed by regex
                        pass

    return variable_dict

if __name__ == "__main__":
    dictionary = extract_dictionary(pdf_path)
    print(f"Extracted {len(dictionary)} variables.")
    
    # Print sample
    print("\nSample variables:")
    for k, v in list(dictionary.items())[:20]:
        print(f"{k}: {v}")
        
    # Save to CSV for reference
    df = pd.DataFrame.from_dict(dictionary, orient='index')
    df.to_csv('data_dictionary.csv')
    print("\nSaved to data_dictionary.csv")
