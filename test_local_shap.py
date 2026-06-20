import os
import time
import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt

start_time = time.time()

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

# Let's say predicted class is Beta Trait (idx 3)
target_class = 3

# base value
ev = explainer.expected_value
if isinstance(ev, np.ndarray) or hasattr(ev, '__len__'):
    base = ev[target_class]
else:
    base = ev

# SHAP values for the target class
class_shap = shap_values[0, :, target_class]

# Generate waterfall plot
plt.figure(figsize=(10, 6))
# Create the explanation object
explanation = shap.Explanation(
    values=class_shap,
    base_values=float(base),
    data=sample_df.iloc[0].values,
    feature_names=ALL_FEATURES
)

# Plot waterfall
shap.plots.waterfall(explanation, max_display=10, show=False)
plt.title(f"Local Explanation for Beta Trait Prediction", fontsize=14, pad=15)
plt.tight_layout()

# Save
os.makedirs('public/images', exist_ok=True)
plt.savefig('public/images/test_waterfall.png', dpi=150, bbox_inches='tight')
plt.close()

end_time = time.time()
print(f"Total time taken: {end_time - start_time:.4f} seconds")
print("Waterfall plot saved to public/images/test_waterfall.png")
