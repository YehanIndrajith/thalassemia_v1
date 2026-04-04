import pandas as pd
import numpy as np
import joblib
import warnings
import os
warnings.filterwarnings('ignore')

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.metrics import recall_score

# Class config
LABEL_MAP = {0: 'Normal', 1: 'Alpha Trait', 2: 'Silent Carrier', 3: 'Beta Trait'}
CLASS_NAMES = ['Normal', 'Alpha Trait', 'Silent Carrier', 'Beta Trait']
RANDOM_STATE = 42
SILENT_CARRIER_IDX = 2

# Derived indices
def add_clinical_indices(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d['Mentzer']         = d['MCV'] / d['RBC']
    d['EnglandFraser']   = (d['MCV'] ** 2 * d['MCH']) / (d['RBC'] * 100)
    d['ShineLal']        = (d['MCV'] ** 2 * d['MCH']) / 100
    d['RDWI']            = (d['RDW'] * d['MCV']) / d['RBC']
    d['GreenKing']       = (d['MCV'] ** 2 * d['RDW']) / (d['HGB'] * 100)
    d['MCHC_MCH_ratio']  = d['MCHC'] / d['MCH']
    d['HGB_RBC_ratio']   = d['HGB'] / d['RBC']
    return d

print("Loading dataset...")
data_path = r'c:\Users\ASUS\Desktop\Thal\thalassemia_levels_prediction\thal final dataset new.xlsx'
df = pd.read_excel(data_path)
df.columns = df.columns.str.strip()

CBC_FEATURES = ['RBC', 'HGB', 'MCV', 'MCH', 'MCHC', 'RDW']
df = add_clinical_indices(df)
DERIVED_FEATURES = ['Mentzer', 'EnglandFraser', 'ShineLal', 'RDWI', 'GreenKing', 'MCHC_MCH_ratio', 'HGB_RBC_ratio']
ALL_FEATURES = CBC_FEATURES + DERIVED_FEATURES

X = df[ALL_FEATURES].copy()
y = df['Label'].copy()

X = X.fillna(X.median())

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)

print("Training Random Forest directly (user's best model)...")
best_model = RandomForestClassifier(n_estimators=300, class_weight='balanced', random_state=RANDOM_STATE, n_jobs=-1)
best_model.fit(X_train_sc, y_train)

os.makedirs('ml_model', exist_ok=True)
joblib.dump(best_model, 'ml_model/model.pkl')
joblib.dump(scaler, 'ml_model/scaler.pkl')

print("Model and scaler saved to ml_model/")
