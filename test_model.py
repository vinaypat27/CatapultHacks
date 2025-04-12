# test_model.py

import joblib
import re
from collections import Counter

# Load trained components
model = joblib.load("compliance_model.joblib")
vectorizer = joblib.load("compliance_vectorizer.joblib")
categories = joblib.load("compliance_categories.joblib")

def check_compliance(text, model, vectorizer, categories):
    # Split text into logical clauses
    clauses = re.split(r'\n+|\.\s+', text)
    clauses = [clause.strip() for clause in clauses if len(clause.strip()) > 30]

    if not clauses:
        return 0, [], "No valid clauses found in text."

    # Vectorize clauses
    X_input = vectorizer.transform(clauses)
    preds = model.predict(X_input)

    # Determine matched compliance categories
    matched_categories = set()
    for pred in preds:
        if pred in categories:
            matched_categories.add(pred)

    # Compute score
    matched_count = len(matched_categories)
    total_possible = len(categories)
    compliance_score = round((matched_count / total_possible) * 10, 2)

    # Breakdown of all predictions
    category_counts = Counter(preds)

    return compliance_score, sorted(list(matched_categories)), dict(category_counts)

# 🔍 Example test input
if __name__ == "__main__":
    test_text = """
    This agreement shall be governed by the laws of the State of California.
    The Company agrees to maintain insurance during the term of the contract.
    Either party may terminate the agreement with 30 days’ notice.
    The contract becomes effective on January 1, 2024 and expires December 31, 2025.
    """

    score, matched, breakdown = check_compliance(test_text, model, vectorizer, categories)

    print(f"\n✅ Compliance Score: {score}/10")
    print(f"✅ Matched Categories: {matched}")
    print(f"📊 Full Prediction Breakdown:\n{breakdown}")
