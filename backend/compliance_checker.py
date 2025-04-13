import joblib
import re
import sys
import json
from domain_config import DOMAIN_CATEGORIES, DOMAIN_KEYWORDS
import PyPDF2

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Load model and assets
model = joblib.load("compliance_model_v3.joblib")
vectorizer = joblib.load("compliance_vectorizer_v3.joblib")
all_categories = joblib.load("compliance_categories_v3.joblib")
keyword_patterns = joblib.load("keyword_patterns_v3.joblib")

def detect_domain(text):
    domain_scores = {}

    for domain, patterns in DOMAIN_KEYWORDS.items():
        score = sum(1 for pattern in patterns if re.search(pattern, text, re.IGNORECASE))
        domain_scores[domain] = score

    # Pick domain with highest score, fallback to 'general' if all scores are 0
    best_match = max(domain_scores, key=domain_scores.get)
    return best_match if domain_scores[best_match] > 0 else "general"

def check_categories(text, categories):
    matched = set()

    # Normalize text
    normalized_text = re.sub(r'\s+', ' ', text).lower()
    # Model prediction
    X = vectorizer.transform([normalized_text])
    pred = model.predict(X)[0]
    if pred in categories:
        matched.add(pred)

    # Keyword fallback
    for cat in categories:
        if cat not in matched and cat in keyword_patterns:
            for pattern in keyword_patterns[cat]:
                if re.search(pattern, normalized_text, re.IGNORECASE):
                    matched.add(cat)
                    # Optional debug logging
                    # print(f"🔍 Matched '{cat}' with pattern: '{pattern}'")
                    break

    unmatched = set(categories) - matched
    
    # Calculate score out of 100 directly
    score = round((len(matched) / len(categories)) * 100, 2) if categories else 0.0

    return {
        "score": score,
        "matched": sorted(matched),
        "unmatched": sorted(unmatched),
        "total_categories": len(categories)
    }

def predict_compliance(text):
    detected_domain = detect_domain(text)
    domain_categories = DOMAIN_CATEGORIES.get(detected_domain, all_categories)

    overall_result = check_categories(text, all_categories)
    domain_result = check_categories(text, domain_categories)

    return {
        "detected_domain": detected_domain,
        "overall_score": overall_result["score"],
        "domain_score": domain_result["score"],
        "overall_matched": overall_result["matched"],
        "overall_unmatched": overall_result["unmatched"],
        "domain_matched": domain_result["matched"],
        "domain_unmatched": domain_result["unmatched"]
    }

# Modified main function to handle command-line arguments
if __name__ == "__main__":
    # Check if file path is provided as command-line argument
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided"}))
        sys.exit(1)
        
    try:
        file_path = sys.argv[1]
        pdf_text = extract_text_from_pdf(file_path)
        result = predict_compliance(pdf_text)
        
        # Output the result as JSON to stdout
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
