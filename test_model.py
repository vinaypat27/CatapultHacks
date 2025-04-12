import joblib
import re

# Load everything
model = joblib.load("compliance_model_v3.joblib")
vectorizer = joblib.load("compliance_vectorizer_v3.joblib")
categories = joblib.load("compliance_categories_v3.joblib")
keyword_patterns = joblib.load("keyword_patterns_v3.joblib")

def predict_compliance(text):
    matched = set()

    # Model prediction
    X = vectorizer.transform([text])
    pred = model.predict(X)[0]
    if pred != 'Non-Compliant':
        matched.add(pred)

    # Keyword fallback
    for cat in categories:
        if cat not in matched and cat in keyword_patterns:
            for pattern in keyword_patterns[cat]:
                if re.search(pattern, text, re.IGNORECASE):
                    matched.add(cat)
                    break

    # Get unmatched categories
    unmatched = set(categories) - matched

    # Score out of 10
    score = round((len(matched) / len(categories)) * 10, 2)
    return score, sorted(matched), sorted(unmatched)

# Example usage
if __name__ == "__main__":
    with open("sample_contract.txt", "r") as f:
        test_text = f.read()

    score, matched, unmatched = predict_compliance(test_text)

    print("\n--------------------------------")
    print("Matched Compliance Categories:\n", matched)

    if (len(unmatched) == 0):
        print("\nAll compliance categories matched")
    else:
        print("\nMissing Compliance Categories:")
        for cat in unmatched:
            print(f"- {cat}")

    print("\nCompliance Score (out of 10):", score)
    print("--------------------------------")