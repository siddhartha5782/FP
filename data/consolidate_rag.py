import os
import json

in_dirs = {
    "advanced_clinical_docs": "d:/FP/data/advanced_clinical_docs",
    "scraped_docs": "d:/FP/data/scraped_docs"
}
out_file = "d:/FP/data/cxr_kb.jsonl"

new_entries = []

for folder_name, dir_path in in_dirs.items():
    if not os.path.exists(dir_path):
        continue
        
    files = [f for f in os.listdir(dir_path) if f.endswith('.md')]
    for file in files:
        topic = file.replace('.md', '')
        with open(os.path.join(dir_path, file), 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Our MD formats all use "## " or "### " to denote sub-headers for Symptoms/Treatments
        # The advanced docs use "### ", the scraped docs use "## 1. ", "## 2. ", etc.
        import re
        # Splitting by either "### " or "## "
        sections = re.split(r'\n##\s+|\n###\s+', '\n' + content)
        
        for sec in sections[1:]: # Skip the first part which is the main title # Topic
            lines = sec.strip().split('\n')
            sub_type = lines[0].strip() # "Clinical Overview", "Symptoms", "Treatment"
            
            # Clean numbered prefixes from scraped docs (e.g. "1. Clinical Overview")
            sub_type = re.sub(r'^\d+\.\s*', '', sub_type)
            
            text_body = "\n".join(lines[1:]).strip()
            text_body = text_body.replace('*Note: Sourced from Mayo Clinic and Cleveland Clinic.*', '').strip()
            text_body = re.sub(r'\n---\n\*.*\n?', '', text_body) # Remove wikipedia footer
            
            sub_id = sub_type.lower().replace(' ', '_').replace('&', 'and').replace('/', '_')
            
            entry = {
                "id": f"{topic}_{sub_id}_{folder_name}",
                "topic": topic,
                "type": sub_type,
                "text": text_body
            }
            if text_body:
               new_entries.append(entry)

with open(out_file, 'a', encoding='utf-8') as f:
    for entry in new_entries:
        f.write(json.dumps(entry) + '\n')

print(f"Successfully processed {len(files)} files and appended {len(new_entries)} advanced clinical chunks into cxr_kb.jsonl!")
