# Autonomous Insurance Claims Processing Agent

This is a lightweight FNOL (First Notice of Loss) processing agent built for the  
Synapx Junior Software Engineer assessment.

The agent processes FNOL documents, extracts key structured fields, validates required information, and routes claims using a priority-based rule engine.

---

## 🚀 Functionality

- Extracts policy, incident, claimant, and asset details from FNOL text (PDF/TXT)
- Detects missing mandatory fields
- Routes claims based on defined business rules
- Provides clear reasoning for each routing decision
- Outputs structured results in JSON format

---

## ⚙️ Design Approach

The system follows a simple processing pipeline:

Extraction → Validation → Routing → Output

Routing is handled using a **priority-based rule engine**:

1. Manual Review (if mandatory fields are missing)
2. Investigation (if fraud-related keywords detected)
3. Specialist Queue (if claim type is injury)
4. Fast-track (if damage < ₹25,000)
5. Standard Processing (default)

---

## 📊 Routing Rules

- Estimated damage below ₹25,000 → Fast-track  
- Missing mandatory fields → Manual review  
- Fraud-related keywords → Investigation  
- Injury-related claims → Specialist queue  

---

## ▶️ How to Run

### 1. Install dependency

pip install pdfplumber


### 2. Run the script

python app.py sample_fnol.txt


---

## 📁 Sample Test Cases

- `sample_fnol.txt` → Fast-track scenario  
- `fraud_case.txt` → Investigation scenario  
- `missing_fields.txt` → Manual review scenario  

---

## 📌 Notes

- FNOL data used is fully synthetic and contains no real personal information  
- Designed with a modular and extensible approach  
- AI tools were used to accelerate development and validate logic  

---
