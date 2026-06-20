import time
start_time = time.time()

import joblib
import pandas as pd
import numpy as np
import shap

# Load model and scaler
model_path = r'ml_model/model.pkl'
scaler_path = r'ml_model/scaler.pkl'

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# Features
CBC_FEATURES = ['RBC', 'HGB', 'MCV', 'MCH', 'MCHC', 'RDW']
DERIVED_FEATURES = ['Mentzer', 'EnglandFraser', 'ShineLal', 'RDWI', 'GreenKing', 'MCHC_MCH_ratio', 'HGB_RBC_ratio']
ALL_FEATURES = CBC_FEATURES + DERIVED_FEATURES

# Test sample
sample_raw = {'RBC': 5.30, 'HGB': 8.7, 'MCV': 49.0, 'MCH': 16.3, 'MCHC': 33.5, 'RDW': 18.2}
sample_df = pd.DataFrame([sample_raw])
# Derived indices
d = sample_df.copy()
d['Mentzer']         = d['MCV'] / d['RBC']
d['EnglandFraser']   = (d['MCV'] ** 2 * d['MCH']) / (d['RBC'] * 100)
d['ShineLal']        = (d['MCV'] ** 2 * d['MCH']) / 100
d['RDWI']            = (d['RDW'] * d['MCV']) / d['RBC']
d['GreenKing']       = (d['MCV'] ** 2 * d['RDW']) / (d['HGB'] * 100)
d['MCHC_MCH_ratio']  = d['MCHC'] / d['MCH']
d['HGB_RBC_ratio']   = d['HGB'] / d['RBC']
sample_df = d

sample_vals = sample_df[ALL_FEATURES].values
sample_sc = scaler.transform(sample_vals)

# Explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(sample_sc)

# Base value
ev = explainer.expected_value

end_time = time.time()
print(f"Time taken to load and compute SHAP: {end_time - start_time:.4f} seconds")
