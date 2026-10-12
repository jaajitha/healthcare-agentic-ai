import os, pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

INPUT = 'agentic_ai_patient_context_15000.csv.xlsx'
OUT = 'trained_models'
os.makedirs(OUT, exist_ok=True)

df = pd.read_excel(INPUT)
df.columns = [c.strip().lower() for c in df.columns]
for c in ['symptoms_text', 'sex', 'prognosis']:
    df[c] = df[c].fillna('').astype(str).str.strip()

# Convert comma-separated symptoms into binary ML features
sets, all_symptoms = [], set()
for text in df['symptoms_text']:
    s = {x.strip() for x in text.split(',') if x.strip()}
    sets.append(s)
    all_symptoms.update(s)

symptoms = sorted(all_symptoms)
X_symptoms = pd.DataFrame([{s: int(s in row) for s in symptoms} for row in sets])

numeric = ['age', 'temperature_c', 'heart_rate_bpm',
           'systolic_bp_mmhg', 'diastolic_bp_mmhg', 'spo2_percent']
X_numeric = df[numeric].apply(pd.to_numeric, errors='coerce')
X_numeric = X_numeric.fillna(X_numeric.median())
X_sex = pd.get_dummies(df['sex'].replace('', 'Unknown'), prefix='sex', dtype=int)

X = pd.concat([X_numeric, X_sex, X_symptoms], axis=1)
encoder = LabelEncoder()
y = encoder.fit_transform(df['prognosis'])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

rf = RandomForestClassifier(
    n_estimators=100, random_state=42,
    class_weight='balanced', n_jobs=-1
)
rf.fit(X_train, y_train)
rf_accuracy = accuracy_score(y_test, rf.predict(X_test))

xgb = XGBClassifier(
    n_estimators=100, max_depth=5, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8,
    objective='multi:softprob', eval_metric='mlogloss',
    random_state=42, n_jobs=2
)
xgb.fit(X_train, y_train)
xgb_accuracy = accuracy_score(y_test, xgb.predict(X_test))

pickle.dump(rf, open(os.path.join(OUT, 'random_forest_model.pkl'), 'wb'))
pickle.dump(xgb, open(os.path.join(OUT, 'xgboost_model.pkl'), 'wb'))
pickle.dump(encoder, open(os.path.join(OUT, 'label_encoder.pkl'), 'wb'))
pickle.dump(list(X.columns), open(os.path.join(OUT, 'feature_columns.pkl'), 'wb'))

print(f'Rows: {len(df)}')
print(f'Features: {X.shape[1]}')
print(f'Classes: {len(encoder.classes_)}')
print(f'Random Forest accuracy: {rf_accuracy:.4f}')
print(f'XGBoost accuracy: {xgb_accuracy:.4f}')
