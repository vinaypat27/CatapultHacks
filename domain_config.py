DOMAIN_CATEGORIES = {
    "general": [],

    "healthcare": [
        "HIPAA", "Insurance", "Compliance", "Protected Health Information"
    ],
    "education": [
        "FERPA", "Effective Date", "Expiration Date", "Academic", "Student"
    ],
    "banking": [
        "GDPR", "Insurance", "Financial Data",
    ],
    "nda": [
        "Non-Compete", "Non-Disparagement", "No-Solicit Of Employees", "Confidential Information", "failure to exercise"
    ],
    "license": [
        "License", "License Agreement", "Intellectual property rights", "Reservation of rights", "Cap On Liability", "Confidentiality", "Indemnification", 
        "License", "Non-Compliant", "Non-Disparagement", "Uncapped Liability"
    ]
}

DOMAIN_KEYWORDS = {
    "healthcare": [r"\bHIPAA\b", r"\bhealth\b", r"\bpatient\b", r"\bmedical\b"],
    "education": [r"\bschool\b", r"\bstudent\b", r"\beducation\b", r"\bFERPA\b"],
    "banking": [r"\bbank\b", r"\bfinancial\b", r"\bcredit\b", r"\bdebit\b", r"\bGDPR\b"],
    "nda": [r"\bconfidentiality\b", r"\bnon-disclosure\b", r"\bnon-compete\b", r"\bno-solicit\b", r"\bNDA\b"],
    "license": [r"\blicense\b", r"\blicense agreement\b", r"\blicensee\b", r"\bintellectual property rights\b", r"\breservation of rights\b"]
}
