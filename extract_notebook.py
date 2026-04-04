import json
import sys

# Load notebook
input_file = r'c:\Users\ASUS\Desktop\Thal\thalassemia_levels_prediction\thalassemia_research.ipynb'
output_file = 'extracted_notebook.py'

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        for cell in nb.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = "".join(cell.get('source', []))
                f.write("# --- CELL ---\n")
                f.write(source)
                f.write("\n\n")
    print("Notebook extracted to " + output_file)
except FileNotFoundError:
    print(f"Error: Could not find '{input_file}'")
except Exception as e:
    print(f"Error extracting notebook: {e}")
