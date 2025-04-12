import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

# Step 1: Load the dataset
df = pd.read_csv("/Users/parthranade/Documents/Hackathon/CUAD_v1/master_clauses.csv")
print(df.columns.tolist())

# Updated categories (based on your column list)
categories = [
    'GDPR', 'HIPAA', 'Insurance', 'Audit Rights', 'Cap On Liability',
    'Uncapped Liability', 'Indemnification', 'Termination For Convenience',
    'Governing Law', 'Effective Date', 'Expiration Date', 'Confidentiality'
]
clause_cols = categories
answer_cols = [f"{cat}-Answer" for cat in categories]

# Build the clause → label dataset
data = []
for i, row in df.iterrows():
    for clause_col, answer_col, cat in zip(clause_cols, answer_cols, categories):
        clause_text = str(row.get(clause_col)).strip()
        answer = str(row.get(answer_col)).strip().lower()
        if clause_text and clause_text != 'nan':
            if answer == 'yes':
                data.append((clause_text, cat))
            elif answer == 'no':
                data.append((clause_text, 'Non-Compliant'))

# Create DataFrame
clause_df = pd.DataFrame(data, columns=['text', 'label'])

# Drop very short or empty text
clause_df = clause_df[clause_df['text'].str.len() > 20]

# DEBUG: Print sample size
print(f"Loaded {len(clause_df)} clause entries for training.")

# Handle empty data edge case
if clause_df.empty:
    raise ValueError("No valid text entries were found. Check your column mappings or data content.")

# Vectorize text
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X = vectorizer.fit_transform(clause_df['text'])
y = clause_df['label']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Predict + evaluate
y_pred = model.predict(X_test)
print("Evaluation Report:\n")
print(classification_report(y_test, y_pred))

'''
# Plot label distribution
clause_df['label'].value_counts().plot(kind='bar', title='Label Distribution')
plt.tight_layout()
plt.show()
'''

def check_compliance(text, model, vectorizer, categories):
    import re
    from collections import Counter

    # Step 1: Split into clauses (simple heuristic)
    clauses = re.split(r'\n+|\.\s+', text)
    clauses = [clause.strip() for clause in clauses if len(clause.strip()) > 30]

    if not clauses:
        return 0, [], "No valid clauses found in text."

    # Step 2: Vectorize
    X_input = vectorizer.transform(clauses)
    preds = model.predict(X_input)

    # Step 3: Count matched compliance categories
    matched_categories = set()
    for pred in preds:
        if pred in categories:
            matched_categories.add(pred)

    # Step 4: Score based on full category coverage
    matched_count = len(matched_categories)
    total_possible = len(categories)

    compliance_score = round((matched_count / total_possible) * 10, 2)

    # Optional: Breakdown
    category_counts = Counter(preds)

    return compliance_score, sorted(list(matched_categories)), dict(category_counts)


# 🔍 Example test
if __name__ == "__main__":
    test_text = """
    This agreement shall be governed by the laws of the State of California.
    The Company agrees to maintain insurance during the term of the contract.
    Either party may terminate the agreement with 30 days notice.
    The contract becomes effective on January 1, 2024 and expires December 31, 2025.
    """
    score, matched, preds = check_compliance(test_text, model, vectorizer, categories)
    print(f"\n Compliance Score: {score}/10")
    print(f" Matched Categories: {matched}")

