# train_model_v2.py

import pandas as pd
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Load the dataset
df = pd.read_csv("/Users/parthranade/Documents/Hackathon/CUAD_v1/master_clauses.csv")

# Define all compliance categories you care about
all_categories = [
    'GDPR', 'HIPAA', 'Insurance', 'Audit Rights', 'Cap On Liability',
    'Uncapped Liability', 'Indemnification', 'Termination For Convenience',
    'Governing Law', 'Effective Date', 'Expiration Date', 'Confidentiality'
]

# Define actual columns present in CSV (base categories)
existing_columns = [col for col in all_categories if f"{col}-Answer" in df.columns]

# 1. Training data from labeled answers
data = []
for i, row in df.iterrows():
    for cat in existing_columns:
        clause_text = str(row.get(cat)).strip()
        answer = str(row.get(f"{cat}-Answer")).strip().lower()

        if clause_text and clause_text.lower() != 'nan':
            if answer == 'yes':
                data.append((clause_text, cat))  # positive class
            elif answer == 'no':
                data.append((clause_text, 'Non-Compliant'))  # negative class

# 2. Add keyword-based training for categories NOT in columns
KEYWORD_PATTERNS = {
    'GDPR': [r'\bGDPR\b', r'General Data Protection Regulation'],
    'HIPAA': [r'\bHIPAA\b', r'Health Insurance Portability and Accountability Act'],
    'Insurance': [r'\binsurance\b', r'coverage', r'certificate of insurance'],
    'Audit Rights': [r'\baudit\b', r'\binspect records\b'],
    'Cap On Liability': [r'\bliability.*(limited|capped)\b'],
    'Uncapped Liability': [r'\bliability.*(not limited|uncapped|unlimited)\b'],
    'Indemnification': [r'\bindemnify\b', r'\bindemnification\b'],
    'Termination For Convenience': [r'\btermination for convenience\b', r'terminate.*without cause'],
    'Governing Law': [r'\bgoverning law\b', r'laws of \w+', r'jurisdiction'],
    'Effective Date': [r'\beffective date\b', r'start date'],
    'Expiration Date': [r'\bexpiration date\b', r'end date', r'termination date'],
    'Confidentiality': [r'\bconfidentiality\b', r'confidential information'],
}

# Only apply keyword search for categories not in existing columns
unlabeled_categories = [cat for cat in all_categories if cat not in existing_columns]

for i, row in df.iterrows():
    text_block = " ".join([str(row.get(col)) for col in df.columns if isinstance(row.get(col), str)])

    for cat in unlabeled_categories:
        patterns = KEYWORD_PATTERNS.get(cat, [])
        if any(re.search(pattern, text_block, re.IGNORECASE) for pattern in patterns):
            data.append((text_block, cat))

# 3. Create DataFrame
clause_df = pd.DataFrame(data, columns=['text', 'label'])
clause_df = clause_df[clause_df['text'].str.len() > 20]  # Filter short/empty texts

print(f"✅ Total clauses used for training: {len(clause_df)}")

# 4. Vectorize
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X = vectorizer.fit_transform(clause_df['text'])
y = clause_df['label']

# 5. Split and train
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 6. Evaluate
y_pred = model.predict(X_test)
print("\n📊 Evaluation Report:\n")
print(classification_report(y_test, y_pred))

# 7. Save model, vectorizer, labels
joblib.dump(model, "compliance_model_v2.joblib")
joblib.dump(vectorizer, "compliance_vectorizer_v2.joblib")
joblib.dump(all_categories, "compliance_categories_v2.joblib")

print("Model, vectorizer, and category list saved.")
