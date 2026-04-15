import sys
import os
import re
import json
import pdfplumber


def load_text_from_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    _, ext = os.path.splitext(path.lower())

    if ext == ".pdf":
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
        return "\n".join(text_parts)
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def clean_number(value):
    if value is None:
        return None
    digits = re.sub(r"[^\d\.]", "", value)
    if digits == "":
        return None
    try:
        return float(digits)
    except ValueError:
        return None


def extract_value(patterns, text):
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_fields(text):
    fields = {}

    fields["policyNumber"] = extract_value(
        [r"Policy\s*Number[:\-\s]+([A-Za-z0-9\-\/]+)",
         r"Policy\s*No\.?[:\-\s]+([A-Za-z0-9\-\/]+)"],
        text,
    )

    fields["policyholderName"] = extract_value(
        [r"Policyholder\s*Name[:\-\s]+(.+)",
         r"Insured\s*Name[:\-\s]+(.+)"],
        text,
    )

    fields["policyEffectiveFrom"] = extract_value(
        [r"Effective\s*From[:\-\s]+(.+)",
         r"Policy\s*Effective\s*Date[:\-\s]+(.+)"],
        text,
    )

    fields["policyEffectiveTo"] = extract_value(
        [r"Effective\s*To[:\-\s]+(.+)",
         r"Policy\s*Expiration\s*Date[:\-\s]+(.+)"],
        text,
    )

    fields["incidentDate"] = extract_value(
        [r"Date\s*of\s*Loss[:\-\s]+(.+)",
         r"Incident\s*Date[:\-\s]+(.+)"],
        text,
    )

    fields["incidentTime"] = extract_value(
        [r"Time\s*of\s*Loss[:\-\s]+(.+)",
         r"Incident\s*Time[:\-\s]+(.+)"],
        text,
    )

    fields["incidentLocation"] = extract_value(
        [r"Location[:\-\s]+(.+)",
         r"Loss\s*Location[:\-\s]+(.+)"],
        text,
    )

    fields["incidentDescription"] = extract_value(
        [r"Description\s*of\s*Loss[:\-\s]+(.+)",
         r"Accident\s*Description[:\-\s]+(.+)"],
        text,
    )

    fields["claimantName"] = extract_value(
        [r"Claimant[:\-\s]+(.+)",
         r"Claimant\s*Name[:\-\s]+(.+)"],
        text,
    )

    fields["thirdParties"] = extract_value(
        [r"Third\s*Party[:\-\s]+(.+)",
         r"Other\s*Parties\s*Involved[:\-\s]+(.+)"],
        text,
    )

    fields["contactDetails"] = extract_value(
        [r"Contact\s*Details[:\-\s]+(.+)",
         r"Phone[:\-\s]+(.+)"],
        text,
    )

    fields["assetType"] = extract_value(
        [r"Asset\s*Type[:\-\s]+(.+)",
         r"Vehicle\s*Type[:\-\s]+(.+)"],
        text,
    )

    fields["assetId"] = extract_value(
        [r"Asset\s*ID[:\-\s]+(.+)",
         r"Vehicle\s*ID[:\-\s]+(.+)",
         r"VIN[:\-\s]+(.+)"],
        text,
    )

    estimated_damage_raw = extract_value(
        [r"Estimated\s*Damage[:\-\s]+(.+)",
         r"Damage\s*Estimate[:\-\s]+(.+)",
         r"Initial\s*Estimate[:\-\s]+(.+)"],
        text,
    )

    fields["estimatedDamage"] = clean_number(estimated_damage_raw)

    fields["claimType"] = extract_value(
        [r"Claim\s*Type[:\-\s]+(.+)",
         r"Type\s*of\s*Loss[:\-\s]+(.+)"],
        text,
    )

    fields["attachments"] = extract_value(
        [r"Attachments[:\-\s]+(.+)",
         r"Attached\s*Documents[:\-\s]+(.+)"],
        text,
    )

    fields["initialEstimate"] = clean_number(
        extract_value([r"Initial\s*Estimate[:\-\s]+(.+)"], text)
    )

    return fields


def detect_missing_fields(fields):
    mandatory_keys = [
        "policyNumber",
        "policyholderName",
        "policyEffectiveFrom",
        "policyEffectiveTo",
        "incidentDate",
        "incidentTime",
        "incidentLocation",
        "incidentDescription",
        "claimantName",
        "claimType",
        "estimatedDamage",
        "attachments",
        "initialEstimate",
    ]

    return [key for key in mandatory_keys if not fields.get(key)]


def detect_investigation_flag(fields):
    description = (fields.get("incidentDescription") or "").lower()
    return any(word in description for word in ["fraud", "inconsistent", "staged"])


def decide_route(fields, missing_fields):
    estimated_damage = fields.get("estimatedDamage")
    claim_type = (fields.get("claimType") or "").lower()
    investigation_flag = detect_investigation_flag(fields)

    # Priority-based routing
    if missing_fields:
        return (
            "Manual review",
            f"Missing mandatory fields: {', '.join(missing_fields)}"
        )

    if investigation_flag:
        return (
            "Investigation",
            "Description contains fraud-related keywords (fraud/inconsistent/staged)"
        )

    if "injury" in claim_type:
        return (
            "Specialist queue",
            "Claim type is injury and requires specialist handling"
        )

    if estimated_damage is not None and estimated_damage < 25000:
        return (
            "Fast-track",
            "Estimated damage is below ₹25,000"
        )

    return (
        "Standard processing",
        "No special conditions matched"
    )


def build_output(fields, missing_fields, recommended_route, reasoning):
    return {
        "extractedFields": fields,
        "missingFields": missing_fields,
        "recommendedRoute": recommended_route,
        "reasoning": reasoning,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python app.py <path_to_fnol_file>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        text = load_text_from_file(path)
        fields = extract_fields(text)
        missing_fields = detect_missing_fields(fields)
        recommended_route, reasoning = decide_route(fields, missing_fields)

        result = build_output(fields, missing_fields, recommended_route, reasoning)
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
