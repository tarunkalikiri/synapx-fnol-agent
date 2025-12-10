# Autonomous Insurance Claims Processing Agent

This is a lightweight FNOL (First Notice of Loss) processing agent built for the
Synapx Junior Software Engineer assessment.

The agent processes an FNOL document, extracts key fields, validates required
information, and routes the claim using clear, rule-based logic.

## Functionality
- Extracts policy, incident, claimant, and asset details from FNOL text
- Detects missing mandatory fields
- Routes claims based on business rules
- Provides a clear explanation for each routing decision
- Outputs results in JSON format

## Routing Rules
- Estimated damage below 25,000 → Fast-track
- Missing mandatory fields → Manual review
- Fraud-related keywords → Investigation flag
- Injury-related claims → Specialist queue

## How to Run
1. Install dependency:

pip install pdfplumber


2. Run the script:


python app.py sample_fnol.txt


The output will be printed as a JSON object in the terminal.

## Notes
- The FNOL data used is fully synthetic and contains no real personal information.
- AI tools were used to accelerate implementation and validate logic.
