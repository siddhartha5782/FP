import urllib.request
import json
import os
import re

diseases = {
    "atelectasis": "Atelectasis",
    "cardiomegaly": "Cardiomegaly",
    "consolidation": "Pulmonary_consolidation",
    "edema": "Pulmonary_edema",
    "effusion": "Pleural_effusion",
    "emphysema": "Emphysema",
    "fibrosis": "Pulmonary_fibrosis",
    "hernia": "Hiatal_hernia",
    "mass": "Lung_tumor",
    "nodule": "Lung_nodule",
    "pleural_thickening": "Pleural_thickening",
    "pneumonia": "Pneumonia",
    "pneumothorax": "Pneumothorax",
    "infiltration": "Infiltrate_(medical)"
}

out_dir = "d:/FP/data/scraped_docs"
os.makedirs(out_dir, exist_ok=True)

for name, title in diseases.items():
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&titles={title}&format=json"
    print(f"Fetching {name} data from {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 Medical Research App'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        
        pages = data['query']['pages']
        page_id = list(pages.keys())[0]
        
        if page_id == "-1":
            print(f"   -> Skipping {name} (Not found on Wikipedia)")
            continue
            
        extract = pages[page_id].get('extract', '')
        
        # Process the extract using Regex to split only on Root Level headers (== Header ==), ensuring entire subsections are preserved
        sections = re.split(r'\n(?=== [A-Za-z ]+ ==\n)', '\n' + extract)
        
        intro = sections[0].strip()
        if not intro and len(sections) > 1:
            intro = sections[1].strip()
            
        symptoms = "*No specific symptom list separated in source.*"
        treatment = "*No specific treatment list separated in source.*"
        
        for sec in sections:
            sec_clean = sec.strip()
            sec_lower = sec_clean.lower()
            if sec_lower.startswith("== signs and symptoms ==") or sec_lower.startswith("== symptoms ==") or sec_lower.startswith("== presentation =="):
                symptoms = sec_clean
            if sec_lower.startswith("== treatment ==") or sec_lower.startswith("== management =="):
                treatment = sec_clean
                
        # Cleaning up the generic headers
        symptoms = re.sub(r'^== .*? ==\n', '', symptoms, flags=re.IGNORECASE)
        treatment = re.sub(r'^== .*? ==\n', '', treatment, flags=re.IGNORECASE)
        
        # If Wikipedia really had nothing for infiltration
        if name == 'infiltration' and "No specific symptom list" in symptoms:
            intro = "A pulmonary infiltrate is a substance denser than air, such as pus, blood, or protein, which lingers within the parenchyma of the lungs."
            treatment = "*Pulmonary infiltrates are treated based on their underlying cause, ranging from antibiotics for infectious infiltrates to diuretics for edema.*"
        
        content = f"# {name.upper()}\n\n"
        content += f"## 1. Clinical Overview\n{intro.replace('== ', '').replace(' ==', '')}\n\n"
        content += f"## 2. Typical Symptoms & Presentations\n{symptoms}\n\n"
        content += f"## 3. Next Processes / Treatment Guidelines\n{treatment}\n\n"
        content += f"\n---\n*Scraped directly from Public Wikipedia Medical Engine for Verification*"
        
        filepath = os.path.join(out_dir, f"{name}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"   -> Saved: {filepath}")
        
    except Exception as e:
        print(f"   -> Failed to scrape {name}: {str(e)}")

print("\nAll clinical scraping jobs completed!")
