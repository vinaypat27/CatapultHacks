import joblib
import re
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

    # Model prediction
    X = vectorizer.transform([text])
    pred = model.predict(X)[0]
    if pred in categories:
        matched.add(pred)

    # Keyword fallback
    for cat in categories:
        if cat not in matched and cat in keyword_patterns:
            for pattern in keyword_patterns[cat]:
                if re.search(pattern, text, re.IGNORECASE):
                    matched.add(cat)
                    break

    unmatched = set(categories) - matched
    score = round((len(matched) / len(categories)) * 10, 2) if categories else 0.0

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

# Example usage
if __name__ == "__main__":
    pdf_text = extract_text_from_pdf("/Users/parthranade/Documents/Hackathon/CUAD_v1/full_contract_pdf/Part_I/License_Agreements/AlliedEsportsEntertainmentInc_20190815_8-K_EX-10.19_11788293_EX-10.19_Content License Agreement.pdf")
    
    with open("sample_contract.txt", "w") as f:
        f.write(pdf_text)

    result = predict_compliance(pdf_text)

    print("\n--------------------------------")
    print(f"Detected Domain: {result['detected_domain'].title()}")
    print(f"Domain Score: {result['domain_score']} / 10")
    print(f"Overall Score: {result['overall_score']} / 10")

    print("\nMatched (Domain):", result["domain_matched"])
    print("Unmatched (Domain):", result["domain_unmatched"])

    print("\nMatched (Overall):", result["overall_matched"])
    print("Unmatched (Overall):", result["overall_unmatched"])
    print("--------------------------------")