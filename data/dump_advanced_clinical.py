import os

out_dir = "d:/FP/data/advanced_clinical_docs"
os.makedirs(out_dir, exist_ok=True)

docs = {}

docs['atelectasis'] = """# ATELECTASIS

### Clinical Overview
Atelectasis is a condition where the tiny air sacs in the lungs (alveoli) lose air and fail to inflate properly, leading to a partial or complete collapse of a lung or a section (lobe) of a lung.

### Symptoms
Atelectasis often causes no symptoms if only a small area of the lung is affected. When it affects a larger area, symptoms may include:
*   Difficulty breathing or shortness of breath (dyspnea)
*   Rapid, shallow breathing (tachypnea)
*   Coughing
*   Chest pain
*   Bluish skin or lips (signaling low blood oxygen)

### Treatment
Treatment focuses on addressing the underlying cause of the collapse and helping the lung re-expand.
*   **Deep Breathing Exercises:** Using an incentive spirometer and performing deep coughing techniques.
*   **Airway Clearance:** Chest physical therapy (positioning the body with the head lower than the chest, or percussion/clapping) can help loosen secretions.
*   **Clearing Blockages:** If a blockage is identified (tumor or foreign object), procedures like bronchoscopy may be used to clear the airway.
*   **Treating the Cause:** If caused by an underlying issue like a tumor or infection, that condition must be treated (e.g., through medication, surgery).

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['cardiomegaly'] = """# CARDIOMEGALY

### Clinical Overview
Cardiomegaly, or an enlarged heart, isn't a disease itself but a sign of another condition. The heart has to pump harder than usual, which causes the heart muscle to thicken or the chambers to dilate.

### Symptoms
In some people, an enlarged heart causes no signs or symptoms. Others may have:
* Shortness of breath
* Abnormal heart rhythm (arrhythmia)
* Swelling (edema) in the legs and feet
* Weight gain
* Fatigue
* Palpitations or a skipping heartbeat

### Treatment
Treatments focus on the underlying cause:
* **Medications:** Diuretics, ACE inhibitors, Angiotensin II receptor blockers (ARBs), Beta blockers.
* **Medical devices:** A pacemaker to coordinate heart contractions, or an implantable cardioverter-defibrillator (ICD).
* **Surgery:** Heart valve surgery, Coronary bypass surgery, or Left ventricular assist device (LVAD).

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['consolidation'] = """# PULMONARY CONSOLIDATION

### Clinical Overview
Pulmonary consolidation occurs when the normally air-filled spaces (alveoli) become filled with fluid, pus, blood, cells, or other material. It is a radiologic sign of an underlying condition that requires investigation.

### Symptoms
Symptoms depend on the underlying cause, but commonly include:
*   Difficulty breathing or shortness of breath.
*   Cough, which may be dry or productive (thick, green, or bloody phlegm).
*   Chest pain, particularly when breathing deeply or coughing.
*   Fever and chills (frequently seen in infectious causes like pneumonia).
*   Fatigue.

### Treatment
Treatment is entirely dependent on addressing the root cause:
*   **Infections (e.g., pneumonia):** Typically treated with appropriate antibiotics, antivirals, or antifungals.
*   **Pulmonary edema:** Involves medications to manage fluid overload, reduce pressure, or support heart function.
*   **Pulmonary hemorrhage:** Management may include treating the underlying cause, often with steroids.
*   **Supportive care:** Supplemental oxygen, fluids, and pain management.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['edema'] = """# PULMONARY EDEMA

### Clinical Overview
Pulmonary edema is an abnormal buildup of fluid in the air sacs (alveoli) of the lungs. This fluid accumulation makes it difficult for the lungs to exchange oxygen and carbon dioxide. Acute pulmonary edema is a life-threatening medical emergency.

### Symptoms
*   **Sudden (Acute):** Extreme shortness of breath, a feeling of suffocation, coughing producing frothy/pink sputum, wheezing, cold clammy skin.
*   **Long-term (Chronic):** Difficulty breathing during physical activity or when lying flat, waking up at night breathless, rapid weight gain, swelling in legs.

### Treatment
Treatment depends on the underlying cause and severity:
*   **Emergency Medical Care:** Supplemental oxygen or mechanical ventilation.
*   **Medications:** Diuretics to remove excess fluid, Blood Pressure Medications.
*   **Heart-Strengthening Medications:** To improve the heart's pumping ability.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['effusion'] = """# PLEURAL EFFUSION

### Clinical Overview
Pleural effusion, often referred to as "water on the lungs," is an excessive accumulation of fluid in the pleural space—the area between the thin membranes that line your lungs and the inside of your chest cavity.

### Symptoms
*   Shortness of breath (dyspnea), especially with exertion.
*   Chest pain described as "pleuritic" pain, which worsens when taking a deep breath or coughing.
*   Dry, non-productive cough.
*   Orthopnea (Difficulty breathing unless sitting upright).
*   Fever (if caused by an infection).

### Treatment
*   **Treating the underlying cause:** Managing heart failure, cirrhosis, or kidney disease if it is a transudative effusion.
*   **Drainage procedures:** Thoracentesis (needle insertion to drain fluid) or a chest tube for continuous drainage.
*   **Pleurodesis:** A procedure to seal the pleural space and prevent fluid from returning.
*   **Surgery:** If necessary for severe or chronic cases.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['emphysema'] = """# EMPHYSEMA

### Clinical Overview
Emphysema is a chronic, progressive lung condition (a form of COPD) involving damage to the air sacs (alveoli). The inner walls of the alveoli weaken and rupture, creating fewer, larger air spaces. This traps air in the lungs.

### Symptoms
*   Shortness of breath, initially during activity, eventually occurring at rest.
*   Chronic coughing ("smoker's cough").
*   Wheezing or whistling sounds.
*   Chest tightness and heaviness.
*   Fatigue and unintended weight loss in advanced stages.

### Treatment
While emphysema cannot be reversed, treatments slow progression:
*   **Lifestyle:** Smoking cessation and avoiding irritants.
*   **Medications:** Bronchodilators and inhaled corticosteroids.
*   **Therapies:** Pulmonary rehabilitation and supplemental oxygen.
*   **Surgery:** Lung volume reduction surgery, endoscopic valve placement, or lung transplant.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['fibrosis'] = """# PULMONARY FIBROSIS

### Clinical Overview
Pulmonary fibrosis is characterized by scarring (fibrosis) and thickening of the tissue around the air sacs. This damage stiffens the tissue, hindering oxygen exchange into the bloodstream.

### Symptoms
*   Shortness of breath noticeable during or after exertion.
*   Dry, persistent cough.
*   Fatigue and extreme tiredness.
*   Unexplained weight loss.
*   Aching muscles and joints.
*   Clubbing (widening/rounding of the fingertips/toes).

### Treatment
Lung damage is permanent, but treatments aim to slow progression:
*   **Medications:** Anti-fibrotic drugs (pirfenidone and nintedanib).
*   **Immunosuppressants:** Corticosteroids like prednisone to reduce inflammation.
*   **Oxygen Therapy & Rehab:** Supplemental oxygen and pulmonary rehabilitation.
*   **Lung Transplant:** For eligible advanced patients.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['hernia'] = """# HIATAL HERNIA

### Clinical Overview
A hiatal hernia occurs when the upper part of your stomach pushes up through your diaphragm and into your chest region. Large hiatal hernias can allow food and acid to back up into the esophagus (GERD).

### Symptoms
Small hiatal hernias typically cause no symptoms. Larger ones can cause:
* Heartburn
* Regurgitation of food or liquids into the mouth
* Backflow of stomach acid into the esophagus (acid reflux)
* Difficulty swallowing
* Chest or abdominal pain
* Feeling full soon after you eat

### Treatment
* **Medications:** Antacids, H-2 receptor blockers, Proton pump inhibitors to reduce stomach acid.
* **Surgery:** Used when medications don't help, involving pulling the stomach back down into the abdomen and reinforcing the valve at the bottom of the esophagus.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['infiltration'] = """# PULMONARY INFILTRATION

### Clinical Overview
A pulmonary infiltrate is a substance—such as pus, blood, protein, or fluid—that lingers within the parenchyma of the lungs and is denser than air. It is a radiographic finding commonly associated with pneumonia, tuberculosis, and other infections.

### Symptoms
Symptoms mirror the underlying condition causing the infiltrate:
* Productive or dry cough
* Fevers, sweats, or chills (if infectious)
* Shortness of breath
* Chest discomfort or localized pain

### Treatment
* **Antibiotics/Antifungals:** For infectious infiltrates like pneumonia.
* **Diuretics:** If the infiltrate is predominantly fluid buildup from cardiac stress.
* **Immunomodulators:** If the underlying etiology is inflammatory or autoimmune.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['mass'] = """# LUNG MASS / TUMOR

### Clinical Overview
A lung mass is an abnormal buildup of tissue (larger than 3 cm). Benign masses grow slowly and don't spread. Malignant (cancerous) masses invade healthy tissue and can metastasize.

### Symptoms
Often discovered incidentally, but symptoms can include:
*   A persistent or worsening cough.
*   Shortness of breath (dyspnea).
*   Chest pain or discomfort.
*   Coughing up blood (hemoptysis).
*   Wheezing, hoarseness, unexplained weight loss or fatigue.

### Treatment
*   **Active Surveillance:** For benign, stable-appearing masses.
*   **Surgery:** To remove suspicious or cancerous tissue (robotic or video-assisted thoracoscopic surgery).
*   **Cancer Treatments:** Radiation Therapy, Chemotherapy, Targeted Therapy, Immunotherapy, or Radiofrequency Ablation.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['nodule'] = """# PULMONARY NODULE

### Clinical Overview
A pulmonary nodule is a small, round shadow or spot on the lung that is 3 centimeters or smaller. The vast majority of nodules are benign (non-cancerous) and are often the result of a past infection or inflammation.

### Symptoms
Pulmonary nodules almost never cause symptoms and are typically found incidentally while running imaging tests for other reasons.

### Treatment
* **Watchful Waiting:** Most nodules require no immediate treatment. Doctors will recommend serial CT scans over months or years to ensure the nodule does not grow.
* **Biopsy/Surgery:** If the nodule exhibits rapid growth or suspicious borders, a biopsy is performed and surgical removal may be indicated.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['pleural_thickening'] = """# PLEURAL THICKENING

### Clinical Overview
Pleural thickening is a medical condition where the pleura (membrane surrounding the lungs) becomes scarred, hardened, or inflamed. This can limit the lung's ability to expand fully. It often results from past lung infections, asbestos exposure, or inflammation.

### Symptoms
*   Shortness of breath (dyspnea) worsening with exertion.
*   Chest pain that may be worse when taking a deep breath or coughing.
*   Persistent cough and fatigue.

### Treatment
There is no cure to reverse established pleural scarring:
*   **Symptom Management:** Focuses on relieving discomfort and improving breathing.
*   **Addressing Underlying Conditions:** Addressing any active infections or malignant disease.
*   **Surgical Options:** Decortication (removing the scarred pleural tissue) to allow the lung to expand in severe cases.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['pneumonia'] = """# PNEUMONIA

### Clinical Overview
Pneumonia is an infection that inflames the air sacs (alveoli) in one or both lungs. The air sacs may fill with fluid or pus, making breathing difficult.

### Symptoms
*   Cough that produces phlegm or pus.
*   Fever, sweating, and shaking chills.
*   Shortness of breath.
*   Chest pain when breathing or coughing.
*   Confusion or changes in mental awareness (especially in older adults).

### Treatment
*   **Antibiotics:** To treat bacterial pneumonia.
*   **Cough Medication:** Used to calm a severe cough to allow rest.
*   **Hospitalization:** For severe cases involving IV antibiotics, oxygen therapy, or mechanical ventilation.
*   **Viral Pneumonia Treatments:** Supportive care and antivirals.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

docs['pneumothorax'] = """# PNEUMOTHORAX

### Clinical Overview
A pneumothorax (collapsed lung) occurs when air leaks into the pleural space between the lung and chest wall. The air pushes on the outside of the lung, causing it to partially or completely collapse.

### Symptoms
*   Sudden, sharp chest pain (often on one side) that worsens with breath.
*   Shortness of breath.
*   Rapid heart rate, fast breathing, fatigue.
*   Cyanosis (bluish skin tint) in severe cases.

### Treatment
*   **Observation:** For small collapses, serial X-rays until the body reabsorbs the air.
*   **Needle Aspiration or Chest Tube:** A tube is inserted into the air-filled space to continuously remove air.
*   **Surgery:** If it doesn't re-expand, a pleurodesis or video-assisted thoracoscopic surgery is used to seal leaks.
*   **Supplemental Oxygen:** To speed up air reabsorption.

*Note: Sourced from Mayo Clinic and Cleveland Clinic.*
"""

for name, content in docs.items():
    with open(f"{out_dir}/{name}.md", "w") as f:
        f.write(content)

print(f"Successfully generated {len(docs)} clinical documents sourced from Mayo & Cleveland clinics.")
