import pandas as pd
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Load your dataset
df = pd.read_csv("/Users/parthranade/Documents/Hackathon/CUAD_v1/master_clauses.csv")

# Extract all available compliance categories from columns ending in -Answer
answer_columns = [col for col in df.columns if col.endswith("-Answer")]
all_categories = [col.replace("-Answer", "") for col in answer_columns]

# Define keyword patterns for all categories you want to fall back on
KEYWORD_PATTERNS = {
    'GDPR': [r'\bGDPR\b', r'General Data Protection Regulation'],
    'HIPAA': [r'\bHIPAA\b', r'Health Insurance Portability and Accountability Act'],
    'Confidentiality': [r'\bconfidentiality\b', r'confidential information'],
    'Effective Date': [r'\beffective date\b', r'start date'],
    'Expiration Date': [r'\bexpiration date\b', r'end date', r'termination date'],
    'Indemnification': [r'\bindemnify\b', r'\bindemnification\b'],
    'Cap On Liability': [r'\bliability.*(limited|capped)\b'],
    'Uncapped Liability': [r'\bliability.*(not limited|uncapped|unlimited)\b'],
    'Termination For Convenience': [r'\btermination for convenience\b', r'terminate.*without cause'],
    'Audit Rights': [r'\baudit\b', r'\binspect records\b'],
    'Governing Law': [r'\bgoverning law\b', r'laws of \w+', r'jurisdiction'],
    'Insurance': [r'\binsurance\b', r'coverage', r'certificate of insurance'],
    'Non-Disparagement': [r'\bnon-disparagement\b', r'disparage'],
    'Source Code Escrow': [r'\bsource code escrow\b', r'\bescrow\b'],
    # Add more categories here as needed...
}

# Get labeled training data from the columns
data = []
for _, row in df.iterrows():
    for cat in all_categories:
        clause_text = str(row.get(cat)).strip()
        answer = str(row.get(f"{cat}-Answer")).strip().lower()
        if clause_text and clause_text.lower() != "nan":
            if answer == 'yes':
                data.append((clause_text, cat))  # Positive
            elif answer == 'no':
                data.append((clause_text, 'Non-Compliant'))  # Negative

# Add extra training data for categories that might not have explicit columns
existing_labelled = set(all_categories)
fallback_cats = [cat for cat in KEYWORD_PATTERNS if cat not in existing_labelled]

for _, row in df.iterrows():
    all_text = " ".join([str(val) for val in row if isinstance(val, str)])
    for cat in fallback_cats:
        for pattern in KEYWORD_PATTERNS[cat]:
            if re.search(pattern, all_text, re.IGNORECASE):
                data.append((all_text, cat))
                break  # Only add once per category

# Clean and prep final DataFrame
clause_df = pd.DataFrame(data, columns=['text', 'label'])
clause_df = clause_df[clause_df['text'].str.len() > 20]  # Remove junk/short lines

print(f"✅ Total training samples: {len(clause_df)}")
print(f"📦 Categories: {sorted(set(clause_df['label']))}")

# Vectorization
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X = vectorizer.fit_transform(clause_df['text'])
y = clause_df['label']

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# Model Training
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
print("\n📊 Evaluation Report:\n")
print(classification_report(y_test, y_pred))

# Save all components
joblib.dump(model, "compliance_model_v3.joblib")
joblib.dump(vectorizer, "compliance_vectorizer_v3.joblib")
joblib.dump(all_categories + fallback_cats, "compliance_categories_v3.joblib")
joblib.dump(KEYWORD_PATTERNS, "keyword_patterns_v3.joblib")

print("Model, vectorizer, categories, and keyword patterns saved.")
