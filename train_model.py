# train_model.py

import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Step 1: Load dataset
df = pd.read_csv("/Users/parthranade/Documents/Hackathon/CUAD_v1/master_clauses.csv")

# Step 2: Define relevant compliance categories
categories = [
    'GDPR', 'HIPAA', 'Insurance', 'Audit Rights', 'Cap On Liability',
    'Uncapped Liability', 'Indemnification', 'Termination For Convenience',
    'Governing Law', 'Effective Date', 'Expiration Date', 'Confidentiality'
]

# Step 3: Map category to clause + answer columns
clause_cols = categories
answer_cols = [f"{cat}-Answer" for cat in categories]

# Step 4: Build clause → label data
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

# Step 5: Create DataFrame
clause_df = pd.DataFrame(data, columns=['text', 'label'])
clause_df = clause_df[clause_df['text'].str.len() > 20]  # filter short text

print(f"Total clause entries: {len(clause_df)}")

# Step 6: Vectorize the text
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X = vectorizer.fit_transform(clause_df['text'])
y = clause_df['label']

# Step 7: Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2)

# Step 8: Train the classifier
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Step 9: Evaluate
y_pred = model.predict(X_test)
print("\nEvaluation Report:\n")
print(classification_report(y_test, y_pred))

# Step 10: Save the model and vectorizer
joblib.dump(model, "compliance_model.joblib")
joblib.dump(vectorizer, "compliance_vectorizer.joblib")
joblib.dump(categories, "compliance_categories.joblib")

print("Model, vectorizer, and categories saved.")
