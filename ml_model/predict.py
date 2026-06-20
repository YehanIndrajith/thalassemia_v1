import sys
import json
import os
import warnings

# Ensure Roaming site-packages is in the path for web server execution
sys.path.append(r'C:\Users\ASUS\AppData\Roaming\Python\Python313\site-packages')

import joblib
import pandas as pd
import numpy as np
warnings.filterwarnings('ignore')

# Constants
LABEL_MAP = {0: 'Normal', 1: 'Alpha Trait', 2: 'Silent Carrier', 3: 'Beta Trait'}
CLASS_NAMES = ['Normal', 'Alpha Trait', 'Silent Carrier', 'Beta Trait']
CBC_FEATURES = ['RBC', 'HGB', 'MCV', 'MCH', 'MCHC', 'RDW']

# Add derived clinical indices
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

def main():
    try:
        # Read JSON input from STDIN
        input_data = sys.stdin.read()
        data = json.loads(input_data)
        
        # We need rbc, hgb, mcv, mch, rdw. MCHC can be input or derived.
        rbc = float(data.get('rbc', 0))
        hgb = float(data.get('hb', 0))
        mcv = float(data.get('mcv', 0))
        mch = float(data.get('mch', 0))
        rdw = float(data.get('rdw', 0))
        
        # Calculate MCHC if not provided
        # MCHC (g/dL) = (MCH (pg) / MCV (fL)) * 100
        mchc = float(data.get('mchc', 0))
        if mchc == 0 and mcv > 0:
            mchc = (mch / mcv) * 100
            
        raw = {'RBC': rbc, 'HGB': hgb, 'MCV': mcv, 'MCH': mch, 'MCHC': mchc, 'RDW': rdw}
        row = pd.DataFrame([raw])
        row = add_clinical_indices(row)
        
        DERIVED_FEATURES = ['Mentzer', 'EnglandFraser', 'ShineLal', 'RDWI', 'GreenKing', 'MCHC_MCH_ratio', 'HGB_RBC_ratio']
        ALL_FEATURES = CBC_FEATURES + DERIVED_FEATURES
        row_vals = row[ALL_FEATURES].values
        
        # Load model and scaler
        dir_path = os.path.dirname(os.path.realpath(__file__))
        base_path = os.path.dirname(dir_path)
        model = joblib.load(os.path.join(dir_path, 'model.pkl'))
        scaler = joblib.load(os.path.join(dir_path, 'scaler.pkl'))
        
        row_sc = scaler.transform(row_vals)
        row_sc_df = pd.DataFrame(row_sc, columns=ALL_FEATURES)
        
        pred_class_idx = int(model.predict(row_sc)[0])
        pred_probs = model.predict_proba(row_sc)[0]
        
        predicted_class = LABEL_MAP[pred_class_idx]
        confidence = float(np.max(pred_probs)) * 100
        
        # Compute SHAP values for the predicted class
        import shap
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(row_sc_df)
        
        # Extract expected values and target SHAP array
        ev = explainer.expected_value
        if isinstance(ev, np.ndarray) or hasattr(ev, '__len__'):
            base = float(ev[pred_class_idx])
        else:
            base = float(ev)
            
        # Extract SHAP array per class
        if isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
            class_shap = shap_values[0, :, pred_class_idx]
        elif isinstance(shap_values, list):
            class_shap = shap_values[pred_class_idx][0]
        else:
            class_shap = shap_values[0]
            
        # Build raw SHAP dictionary for web response
        shap_contrib = {ALL_FEATURES[i]: float(class_shap[i]) for i in range(len(ALL_FEATURES))}
        
        # Save local explanation waterfall plot deterministically
        filename = f"waterfall_{rbc:.2f}_{hgb:.2f}_{mcv:.1f}_{mch:.1f}_{mchc:.1f}_{rdw:.1f}.png"
        img_dir = os.path.join(base_path, 'public', 'images')
        os.makedirs(img_dir, exist_ok=True)
        img_path = os.path.join(img_dir, filename)
        
        if not os.path.exists(img_path):
            plt.figure(figsize=(9, 5.5))
            explanation = shap.Explanation(
                values=class_shap,
                base_values=base,
                data=row.iloc[0].values,
                feature_names=ALL_FEATURES
            )
            shap.plots.waterfall(explanation, max_display=10, show=False)
            plt.title(f"Local Explanation: {predicted_class} Prediction", fontsize=13, pad=12)
            plt.tight_layout()
            plt.savefig(img_path, dpi=120, bbox_inches='tight')
            plt.close()
        
        # Carrier probability is sum of trait probabilities (Alpha + Silent Carrier + Beta)
        carrier_prob = float(pred_probs[1] + pred_probs[2] + pred_probs[3])
        is_carrier = carrier_prob >= 0.50
        
        # Flag for review if top two classes are close
        sorted_probs = np.sort(pred_probs)[::-1]
        uncertain = (sorted_probs[0] - sorted_probs[1]) < 0.15
        
        # Mentzer index
        mentzer_idx = float(mcv / rbc) if rbc > 0 else 0
        mentzer_interp = 'Suggests thalassemia' if mentzer_idx < 13 else 'Suggests IDA or normal'
        
        # Instead of a separate ordinal model, we map the predicted class directly to its severity name
        ordinal_severity = predicted_class
        
        result = {
            'predicted_class': predicted_class,
            'confidence': round(confidence, 1),
            'class_probabilities': {
                'Normal': round(float(pred_probs[0]), 4),
                'Alpha Trait': round(float(pred_probs[1]), 4),
                'Silent Carrier': round(float(pred_probs[2]), 4),
                'Beta Trait': round(float(pred_probs[3]), 4)
            },
            'ordinal_severity': ordinal_severity,
            'carrier_probability': round(carrier_prob, 4),
            'is_carrier': bool(is_carrier),
            'flag_for_review': bool(uncertain),
            'mentzer_index': round(mentzer_idx, 3),
            'mentzer_interpretation': mentzer_interp,
            'waterfall_image': f"/images/{filename}",
            'shap_values': shap_contrib,
            'base_value': round(base, 4)
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {"error": str(e)}
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == '__main__':
    main()

