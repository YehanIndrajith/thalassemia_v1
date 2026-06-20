import os
import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt

# Load model and scaler
model_path = r'ml_model/model.pkl'
scaler_path = r'ml_model/scaler.pkl'

print("Loading model and scaler...")
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# Load dataset
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
print("Initializing TreeExplainer and computing SHAP values...")
explainer = shap.TreeExplainer(model)

# For global summary plots, let's take a sample of 1000 records to keep it clean and fast
sample_df = X.sample(n=min(1000, len(X)), random_state=42)
sample_sc = scaler.transform(sample_df.values)

# Create a DataFrame with Scaled values and Feature Names for SHAP to display correctly
sample_sc_df = pd.DataFrame(sample_sc, columns=ALL_FEATURES)

shap_values = explainer.shap_values(sample_sc_df)
# In sklearn Random Forest, TreeExplainer returns a list of shape (n_classes, n_samples, n_features) or array (n_samples, n_features, n_classes)
print(f"SHAP values shape: {np.array(shap_values).shape}")

os.makedirs('public/images', exist_ok=True)

# Generate global importance bar plot (average across all classes)
# Normalize to list of 2D arrays
if isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
    shap_list = [shap_values[:, :, i] for i in range(shap_values.shape[2])]
elif isinstance(shap_values, list):
    shap_list = shap_values
else:
    shap_list = [shap_values]

# Mean absolute SHAP values across all classes and samples
mean_shap = np.mean([np.abs(sv) for sv in shap_list], axis=0).mean(axis=0)
shap_importance = pd.DataFrame({
    'Feature': ALL_FEATURES,
    'Mean |SHAP|': mean_shap
}).sort_values('Mean |SHAP|', ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(shap_importance['Feature'], shap_importance['Mean |SHAP|'], color='#58a6ff', edgecolor='none', height=0.6)
plt.title('Global Feature Importance (Mean |SHAP| across all classes)', fontsize=14, pad=15)
plt.xlabel('Mean |SHAP value|')
plt.tight_layout()
plt.savefig('public/images/shap_global_bar.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved public/images/shap_global_bar.png")

# Classes map
CLASS_NAMES = ['Normal', 'Alpha Trait', 'Silent Carrier', 'Beta Trait']

# Generate beeswarm plots for each class
for class_idx, class_name in enumerate(CLASS_NAMES):
    print(f"Generating beeswarm plot for {class_name}...")
    plt.figure(figsize=(10, 6))
    
    # Extract SHAP values for this class
    class_shap = shap_list[class_idx]
    
    # We create an Explanation object for the summary plot
    # This allows beeswarm plot to work and render nicely
    # shap_values can be passed directly to summary_plot
    shap.summary_plot(
        class_shap, 
        sample_sc_df, 
        show=False,
        max_display=10,
        plot_size=None
    )
    
    # Add title and clean up
    plt.title(f'SHAP Beeswarm Plot: {class_name} Prediction Impact', fontsize=14, pad=15)
    plt.tight_layout()
    
    # Save
    safe_name = class_name.replace(' ', '_')
    img_path = f'public/images/shap_beeswarm_{safe_name}.png'
    plt.savefig(img_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved {img_path}")

print("Global SHAP plots generation complete!")
