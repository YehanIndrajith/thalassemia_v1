import os
import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt

# Load model and scaler
model_path = r'ml_model/model.pkl'
scaler_path = r'ml_model/scaler.pkl'

print("Loading model and scaler...")
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

print(f"Model type: {type(model)}")
print(f"Scaler type: {type(scaler)}")

# Test dataset path
dataset_path = r'c:\Users\ASUS\Desktop\Thal\thalassemia_levels_prediction\thal final dataset new.xlsx'
print("Loading dataset...")
df = pd.read_excel(dataset_path)
df.columns = df.columns.str.strip()

CBC_FEATURES = ['RBC', 'HGB', 'MCV', 'MCH', 'MCHC', 'RDW']
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

df = add_clinical_indices(df)
DERIVED_FEATURES = ['Mentzer', 'EnglandFraser', 'ShineLal', 'RDWI', 'GreenKing', 'MCHC_MCH_ratio', 'HGB_RBC_ratio']
ALL_FEATURES = CBC_FEATURES + DERIVED_FEATURES

X = df[ALL_FEATURES].copy()
X = X.fillna(X.median())

# Fit TreeExplainer
print("Initializing TreeExplainer...")
explainer = shap.TreeExplainer(model)

# Test a single sample prediction
sample_raw = {'RBC': 5.30, 'HGB': 8.7, 'MCV': 49.0, 'MCH': 16.3, 'MCHC': 33.5, 'RDW': 18.2}
sample_df = pd.DataFrame([sample_raw])
sample_df = add_clinical_indices(sample_df)
sample_vals = sample_df[ALL_FEATURES].values
sample_sc = scaler.transform(sample_vals)

print("Computing SHAP values for sample...")
shap_values = explainer.shap_values(sample_sc)
print(f"SHAP values computed. Type: {type(shap_values)}, length/shape: {np.array(shap_values).shape}")
