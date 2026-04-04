# --- CELL ---
pip install -r requirements.txt

# --- CELL ---
#!python -m pip install --upgrade pip

# --- CELL ---
#!python -m pip install --upgrade jupyter nbconvert pyzmq

# --- CELL ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Sklearn
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    ConfusionMatrixDisplay, f1_score, recall_score
)
from sklearn.inspection import permutation_importance
# Ordinal regression
from mord import LogisticIT  # pip install mord
# XGBoost
from xgboost import XGBClassifier
import shap

# --- CELL ---
# Plotting config
sns.set_theme(style='whitegrid', palette='muted', font_scale=1.1)
FIGSIZE = (12, 5)
RANDOM_STATE = 42

# Class config
CLASS_NAMES   = ['Normal', 'Alpha Trait', 'Silent Carrier', 'Beta Trait']
LABEL_MAP     = {0: 'Normal', 1: 'Alpha Trait', 2: 'Silent Carrier', 3: 'Beta Trait'}
ORDINAL_MAP   = {0: 0, 2: 1, 1: 2, 3: 3}  # Normal < Silent < Alpha < Beta
ORDINAL_NAMES = ['Normal', 'Silent Carrier', 'Alpha Trait', 'Beta Trait']

# --- CELL ---
df = pd.read_excel('thal final dataset new.xlsx')
df.columns = df.columns.str.strip()

print(f'Shape: {df.shape}')
print(f'\nColumn dtypes:\n{df.dtypes}')
df.head()

# --- CELL ---
print('=== Missing values ===')
print(df.isnull().sum())

print('\n=== Class distribution ===')
dist = df['Label'].value_counts().rename(LABEL_MAP)
print(dist)
print(f'\nClass balance (%):\n{(dist / dist.sum() * 100).round(1)}')

# --- CELL ---
fig, ax = plt.subplots(figsize=(7, 4))
dist.plot(kind='bar', ax=ax, color=sns.color_palette('muted', 4), edgecolor='white')
ax.set_title('Class distribution')
ax.set_xlabel('')
ax.set_ylabel('Count')
ax.tick_params(axis='x', rotation=30)
plt.tight_layout()
plt.show()

# --- CELL ---
CBC_FEATURES = ['RBC', 'HGB', 'MCV', 'MCH', 'MCHC', 'RDW']

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
df_plot = df.copy()
df_plot['Class'] = df_plot['Label'].map(LABEL_MAP)

for ax, feat in zip(axes.flat, CBC_FEATURES):
    sns.violinplot(
        data=df_plot, x='Class', y=feat, ax=ax,
        palette='muted', order=CLASS_NAMES, inner='quartile', linewidth=0.8
    )
    ax.set_title(feat)
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=25)

fig.suptitle('CBC feature distributions by class', fontsize=14, y=1.01)
plt.tight_layout()
plt.show()

# --- CELL ---
fig, ax = plt.subplots(figsize=(8, 6))
corr = df[CBC_FEATURES].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, annot=True, fmt='.2f',
    cmap='coolwarm', center=0, linewidths=0.5, ax=ax
)
ax.set_title('CBC feature correlation matrix')
plt.tight_layout()
plt.show()

# --- CELL ---
# Statistical tests: Kruskal-Wallis per feature across classes
# Non-parametric — appropriate given unknown distribution of CBC values
print(f'{"Feature":<8}  {"H-stat":>10}  {"p-value":>12}  Significant?')
print('-' * 50)
groups = [df[df['Label'] == lbl][CBC_FEATURES] for lbl in sorted(df['Label'].unique())]
for feat in CBC_FEATURES:
    h, p = stats.kruskal(*[g[feat].dropna() for g in groups])
    sig = '*** YES' if p < 0.001 else ('*  YES' if p < 0.05 else '   NO')
    print(f'{feat:<8}  {h:>10.2f}  {p:>12.4e}  {sig}')

# --- CELL ---
# Silent carrier vs Normal overlap — the hardest classification boundary
# Focus on MCV and MCH which are expected to have the most overlap
sc  = df[df['Label'] == 2]  # Silent carrier
nrm = df[df['Label'] == 0]  # Normal

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
overlap_features = ['MCV', 'MCH', 'HGB']

for ax, feat in zip(axes, overlap_features):
    ax.hist(nrm[feat].dropna(), bins=40, alpha=0.55, label='Normal',         color='steelblue',  density=True)
    ax.hist(sc[feat].dropna(),  bins=40, alpha=0.55, label='Silent carrier', color='darkorange', density=True)
    ax.set_title(f'{feat} — Normal vs Silent Carrier')
    ax.legend()

fig.suptitle('Overlap analysis: hardest classification boundary', fontsize=13)
plt.tight_layout()
plt.show()

# Bhattacharyya overlap coefficient (proxy for class separability)
def bhattacharyya_overlap(a, b, bins=50):
    lo, hi = min(a.min(), b.min()), max(a.max(), b.max())
    ha, _ = np.histogram(a, bins=bins, range=(lo, hi), density=True)
    hb, _ = np.histogram(b, bins=bins, range=(lo, hi), density=True)
    return float(np.sum(np.sqrt(ha * hb)) * (hi - lo) / bins)

print('\nOverlap coefficient (0=distinct, 1=identical):')
for feat in CBC_FEATURES:
    ov = bhattacharyya_overlap(nrm[feat].dropna().values, sc[feat].dropna().values)
    print(f'  {feat:<6}: {ov:.3f}')

# --- CELL ---
def add_clinical_indices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Yehan ask her to find references for this, or else I can give what I found
    """
    d = df.copy()

    # Mentzer index  (MCV / RBC)
    # <13 → thalassemia trait;  >13 → iron deficiency
    d['Mentzer']         = d['MCV'] / d['RBC']

    # England & Fraser index  (MCV² × MCH / RBC / 100)
    # Negative → thalassemia;  Positive → iron deficiency
    d['EnglandFraser']   = (d['MCV'] ** 2 * d['MCH']) / (d['RBC'] * 100)

    # Shine & Lal index  (MCV² × MCH / 100)
    # <1530 → thalassemia trait
    d['ShineLal']        = (d['MCV'] ** 2 * d['MCH']) / 100

    # RDWI (RBC Distribution Width Index)  (RDW × MCV / RBC)
    # Higher in thalassemia; helps separate from IDA
    d['RDWI']            = (d['RDW'] * d['MCV']) / d['RBC']

    # Green & King index  (MCV² × RDW / HGB / 100)
    # <65 → thalassemia
    d['GreenKing']       = (d['MCV'] ** 2 * d['RDW']) / (d['HGB'] * 100)

    # MCHC / MCH ratio — separates microcytic anaemias
    d['MCHC_MCH_ratio']  = d['MCHC'] / d['MCH']

    # HGB / RBC  (mean cell haemoglobin content proxy)
    d['HGB_RBC_ratio']   = d['HGB'] / d['RBC']

    return d


df = add_clinical_indices(df)

DERIVED_FEATURES = [
    'Mentzer', 'EnglandFraser', 'ShineLal',
    'RDWI', 'GreenKing', 'MCHC_MCH_ratio', 'HGB_RBC_ratio'
]
ALL_FEATURES = CBC_FEATURES + DERIVED_FEATURES

print('Derived indices added:')
df[DERIVED_FEATURES + ['Label']].groupby('Label').mean().rename(index=LABEL_MAP).round(3)

# --- CELL ---
fig, axes = plt.subplots(2, 4, figsize=(18, 8))
df_plot = df.copy()
df_plot['Class'] = df_plot['Label'].map(LABEL_MAP)

for ax, feat in zip(axes.flat, DERIVED_FEATURES + ['RDW']):
    sns.boxplot(
        data=df_plot, x='Class', y=feat, ax=ax,
        palette='muted', order=CLASS_NAMES, linewidth=0.8, fliersize=2
    )
    ax.set_title(feat)
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=25)

fig.suptitle('Clinical discriminant indices by class', fontsize=14, y=1.01)
plt.tight_layout()
plt.show()

# --- CELL ---
FEATURE_COLS = ALL_FEATURES  # 13 features total

X = df[FEATURE_COLS].copy()
y = df['Label'].copy()  # 0=Normal, 1=Alpha, 2=Silent, 3=Beta

# Impute any remaining NaN with median (shouldn't be many after Age exclusion)
X = X.fillna(X.median())

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

print(f'Train: {X_train.shape[0]} samples')
print(f'Test:  {X_test.shape[0]} samples')
print(f'\nTrain class distribution:')
print(y_train.value_counts().rename(LABEL_MAP))
print(f'\nTest class distribution:')
print(y_test.value_counts().rename(LABEL_MAP))

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

print('\nStratified split + scaling complete.')

# --- CELL ---
y_train_ord = y_train.map(ORDINAL_MAP).values
y_test_ord  = y_test.map(ORDINAL_MAP).values

ordinal_model = LogisticIT()   # Immediate Threshold (proportional odds)
ordinal_model.fit(X_train_sc, y_train_ord)

y_pred_ord = ordinal_model.predict(X_test_sc)

print('=== Ordinal Logistic Regression ===')
print(classification_report(
    y_test_ord, y_pred_ord,
    target_names=ORDINAL_NAMES
))

# --- CELL ---
coef_df = pd.DataFrame({
    'Feature':     FEATURE_COLS,
    'Coefficient': ordinal_model.coef_.flatten()
}).sort_values('Coefficient', key=abs, ascending=False)

print('=== Ordinal Risk Formula Coefficients ===')
print('Thresholds (cut-points):', np.round(ordinal_model.theta_, 4))
print()
print(coef_df.to_string(index=False))

fig, ax = plt.subplots(figsize=(9, 6))
colors = ['tomato' if v > 0 else 'steelblue' for v in coef_df['Coefficient']]
ax.barh(coef_df['Feature'], coef_df['Coefficient'], color=colors, edgecolor='white')
ax.axvline(0, color='black', linewidth=0.8)
ax.set_title('Ordinal logistic regression — feature coefficients\n(positive = higher severity risk)')
ax.set_xlabel('Coefficient (standardised features)')
plt.tight_layout()
plt.show()

# --- CELL ---
print('ORDINAL RISK SCORE FORMULA')
print('=' * 60)
print('Risk_score = ', end='')
terms = []
for _, row in coef_df.iterrows():
    sign = '+' if row['Coefficient'] >= 0 else '-'
    terms.append(f"{sign} {abs(row['Coefficient']):.4f}·{row['Feature']}")
print(' '.join(terms))
print()
print('Classification thresholds (θ):')
boundaries = list(zip(
    ['Normal', 'Silent Carrier', 'Alpha Trait'],
    ['Silent Carrier', 'Alpha Trait', 'Beta Trait'],
    ordinal_model.theta_
))
for lo, hi, t in boundaries:
    print(f'  Risk_score < {t:.4f}  →  {lo}')
print(f'  Risk_score ≥ {ordinal_model.theta_[-1]:.4f}  →  Beta Trait')

# --- CELL ---
y_train_bin = (y_train > 0).astype(int)
y_test_bin  = (y_test  > 0).astype(int)

print(f'Binary distribution — Train:')
print(pd.Series(y_train_bin).value_counts().rename({0: 'Normal', 1: 'Carrier/Trait'}))

bin_lr = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
bin_lr.fit(X_train_sc, y_train_bin)

y_pred_bin  = bin_lr.predict(X_test_sc)
y_prob_bin  = bin_lr.predict_proba(X_test_sc)[:, 1]

print('\n=== Binary Logistic Regression — Carrier vs Normal ===')
print(classification_report(y_test_bin, y_pred_bin, target_names=['Normal', 'Carrier/Trait']))
print(f'ROC-AUC: {roc_auc_score(y_test_bin, y_prob_bin):.4f}')

# --- CELL ---
bin_coef_df = pd.DataFrame({
    'Feature':     FEATURE_COLS,
    'Coefficient': bin_lr.coef_.flatten()
}).sort_values('Coefficient', key=abs, ascending=False)

print('BINARY CARRIER DETECTION FORMULA')
print('=' * 60)
print(f'Intercept: {bin_lr.intercept_[0]:.4f}')
print('Log-odds = intercept', end='')
for _, row in bin_coef_df.iterrows():
    sign = ' +' if row['Coefficient'] >= 0 else ' -'
    print(f'{sign} {abs(row["Coefficient"]):.4f}·{row["Feature"]}', end='')
print('\n')
print('P(Carrier) = sigmoid(Log-odds)')
print('Flag for review if P(Carrier) > 0.50')

from sklearn.metrics import RocCurveDisplay
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

RocCurveDisplay.from_predictions(
    y_test_bin, y_prob_bin, ax=axes[0],
    name='Binary LR', color='steelblue'
)
axes[0].plot([0,1],[0,1],'k--',lw=0.8)
axes[0].set_title('ROC curve — Carrier vs Normal')

cm = confusion_matrix(y_test_bin, y_pred_bin)
ConfusionMatrixDisplay(cm, display_labels=['Normal','Carrier/Trait']).plot(ax=axes[1], colorbar=False)
axes[1].set_title('Confusion matrix — Binary')

plt.tight_layout()
plt.show()

# --- CELL ---
models = {
    'Logistic Regression':  LogisticRegression(max_iter=1000,
        class_weight='balanced', random_state=RANDOM_STATE
    ),
    'SVM':                   SVC(
        kernel='rbf', probability=True,
        class_weight='balanced', random_state=RANDOM_STATE
    ),
    'Random Forest':         RandomForestClassifier(
        n_estimators=300, class_weight='balanced',
        random_state=RANDOM_STATE, n_jobs=-1
    ),
    'Gradient Boosting':     GradientBoostingClassifier(
        n_estimators=200, learning_rate=0.1,
        random_state=RANDOM_STATE
    ),
    'XGBoost':               XGBClassifier(
        n_estimators=300, use_label_encoder=False,
        eval_metric='mlogloss', random_state=RANDOM_STATE,
        n_jobs=-1, verbosity=0
    ),
}

print(f'Models to train: {list(models.keys())}')

# --- CELL ---
# 5-fold stratified CV for all models
# Silent carrier = label 2 in original encoding
SILENT_CARRIER_IDX = 2

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

results = {}
for name, model in models.items():
    print(f'Training {name}...', end=' ', flush=True)
    cv_res = cross_validate(
        model, X_train_sc, y_train,
        cv=cv,
        scoring={
            'accuracy':  'accuracy',
            'f1_macro':  'f1_macro',
            'f1_weighted': 'f1_weighted',
        },
        return_train_score=False,
        n_jobs=-1
    )
    # Silent carrier recall — must compute manually per fold
    sc_recalls = []
    for train_idx, val_idx in cv.split(X_train_sc, y_train):
        m = type(model)(**model.get_params())
        m.fit(X_train_sc[train_idx], y_train.iloc[train_idx])
        preds = m.predict(X_train_sc[val_idx])
        sc_recall = recall_score(
            y_train.iloc[val_idx], preds,
            labels=[SILENT_CARRIER_IDX], average='macro'
        )
        sc_recalls.append(sc_recall)

    results[name] = {
        'accuracy':          cv_res['test_accuracy'].mean(),
        'f1_macro':          cv_res['test_f1_macro'].mean(),
        'f1_weighted':       cv_res['test_f1_weighted'].mean(),
        'sc_recall':         np.mean(sc_recalls),
        'sc_recall_std':     np.std(sc_recalls),
    }
    print(f"done | SC recall: {results[name]['sc_recall']:.3f}")

results_df = pd.DataFrame(results).T.sort_values('sc_recall', ascending=False)
print('\n=== Cross-validation results (sorted by silent carrier recall) ===')
print(results_df.round(4))

# --- CELL ---
metrics_to_plot = ['sc_recall', 'f1_macro', 'f1_weighted', 'accuracy']
metric_labels   = ['Silent Carrier Recall ★', 'Macro F1', 'Weighted F1', 'Accuracy']

fig, axes = plt.subplots(1, 4, figsize=(18, 5), sharey=False)
colors = sns.color_palette('muted', len(results_df))

for ax, metric, label in zip(axes, metrics_to_plot, metric_labels):
    bars = ax.barh(results_df.index, results_df[metric], color=colors, edgecolor='white')
    ax.set_title(label, fontweight='bold' if metric == 'sc_recall' else 'normal')
    ax.set_xlim(0, 1)
    if metric == 'sc_recall':
        ax.axvline(results_df[metric].max(), color='tomato', lw=1, ls='--', alpha=0.6)
    for bar, val in zip(bars, results_df[metric]):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=9)

fig.suptitle('5-fold CV — model comparison (★ = primary metric)', fontsize=13)
plt.tight_layout()
plt.show()

# --- CELL ---
# Fit all models on full training set, evaluate on test set
BEST_MODEL_NAME = results_df.index[0]   # highest SC recall
print(f'Best model by silent carrier recall: {BEST_MODEL_NAME}\n')

test_results = {}
fitted_models = {}
for name, model in models.items():
    model.fit(X_train_sc, y_train)
    fitted_models[name] = model
    y_pred = model.predict(X_test_sc)
    test_results[name] = {
        'sc_recall':   recall_score(y_test, y_pred, labels=[SILENT_CARRIER_IDX], average='macro'),
        'f1_macro':    f1_score(y_test, y_pred, average='macro'),
        'f1_weighted': f1_score(y_test, y_pred, average='weighted'),
        'y_pred':      y_pred,
    }

test_df = pd.DataFrame({k: {m: v for m, v in v.items() if m != 'y_pred'}
                        for k, v in test_results.items()}).T.sort_values('sc_recall', ascending=False)
print('=== Test set results ===')
print(test_df.round(4))

# --- CELL ---
fig, axes = plt.subplots(1, len(models), figsize=(22, 4))
for ax, (name, res) in zip(axes, test_results.items()):
    cm = confusion_matrix(y_test, res['y_pred'])
    disp = ConfusionMatrixDisplay(cm, display_labels=['Norm','Alpha','Silent','Beta'])
    disp.plot(ax=ax, colorbar=False, cmap='Blues')
    sc_rec = res['sc_recall']
    title_color = 'darkgreen' if name == BEST_MODEL_NAME else 'black'
    ax.set_title(f'{name}\nSC recall={sc_rec:.3f}', color=title_color, fontsize=9)
    ax.set_xlabel('')
    ax.set_ylabel('')

fig.suptitle('Test set confusion matrices — Row: true, Col: predicted', y=1.02)
plt.tight_layout()
plt.show()

# --- CELL ---
best_model = fitted_models[BEST_MODEL_NAME]
X_test_df  = pd.DataFrame(X_test_sc, columns=FEATURE_COLS)

# Use TreeExplainer for tree-based models, LinearExplainer otherwise
try:
    explainer = shap.TreeExplainer(best_model)
    shap_values = explainer.shap_values(X_test_df)
except:
    explainer   = shap.LinearExplainer(best_model, X_test_df)
    shap_values = explainer.shap_values(X_test_df)

print(f'SHAP computed for: {BEST_MODEL_NAME}')
print(f'SHAP values shape: {np.array(shap_values).shape}')

# --- CELL ---
# Normalise shap_values to a consistent list-of-2D-arrays format
# XGBoost TreeExplainer returns shape (n_samples, n_features, n_classes) — a 3D array.
# sklearn RF/GB TreeExplainer returns a list of 2D arrays, one per class.
# We normalise both to: list of (n_samples, n_features) arrays.

if isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
    # 3D array → split along last axis
    shap_list = [shap_values[:, :, i] for i in range(shap_values.shape[2])]
elif isinstance(shap_values, list):
    shap_list = shap_values
else:
    # 2D binary case — wrap in list
    shap_list = [shap_values]

n_classes = len(shap_list)
print(f'Classes: {n_classes}, SHAP array shape per class: {shap_list[0].shape}')

# Global feature importance: mean |SHAP| averaged across all classes
mean_shap = np.mean([np.abs(sv) for sv in shap_list], axis=0).mean(axis=0)  # shape: (n_features,)

shap_importance = pd.DataFrame({
    'Feature':    FEATURE_COLS,
    'Mean |SHAP|': mean_shap
}).sort_values('Mean |SHAP|', ascending=False)

fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(shap_importance['Feature'], shap_importance['Mean |SHAP|'],
        color='steelblue', edgecolor='white')
ax.set_title(f'Global feature importance — {BEST_MODEL_NAME}\n(mean |SHAP value| across all classes)')
ax.set_xlabel('Mean |SHAP value|')
ax.invert_yaxis()
plt.tight_layout()
plt.show()

# --- CELL ---
for class_idx, class_name in LABEL_MAP.items():
    if class_idx >= len(shap_list):
        continue
    print(f'\n--- SHAP summary: {class_name} ---')
    shap.summary_plot(
        shap_list[class_idx], X_test_df,
        plot_type='bar', show=False, max_display=10
    )
    plt.title(f'Top features for predicting: {class_name}')
    plt.tight_layout()
    plt.show()

# --- CELL ---
y_pred_best = test_results[BEST_MODEL_NAME]['y_pred']

ev = explainer.expected_value
if np.isscalar(ev):
    ev = [ev] * len(shap_list)

for target_class, class_name in [(2, 'Silent Carrier'), (1, 'Alpha Trait'), (3, 'Beta Trait')]:
    mask = (np.array(y_test) == target_class) & (y_pred_best == target_class)
    idx  = np.where(mask)[0]
    if len(idx) == 0:
        print(f'No correctly predicted {class_name} found — skipping')
        continue
    sample_idx = idx[0]
    print(f'\n=== Local explanation: {class_name} (test idx {sample_idx}) ===')
    
    base = ev[target_class] if hasattr(ev, '__len__') else ev
    
    shap.waterfall_plot(
        shap.Explanation(
            values=shap_list[target_class][sample_idx],
            base_values=float(base),
            data=X_test_df.iloc[sample_idx].values,
            feature_names=FEATURE_COLS
        ),
        max_display=10, show=False
    )
    plt.title(f'Local explanation — predicted {class_name}')
    plt.tight_layout()
    plt.show()

# --- CELL ---
summary_rows = []
for name, res in test_results.items():
    report = classification_report(y_test, res['y_pred'], output_dict=True)
    summary_rows.append({
        'Model':             name,
        'SC Recall ★':       round(res['sc_recall'], 4),
        'Normal Recall':     round(report['0']['recall'], 4),
        'Alpha Recall':      round(report['1']['recall'], 4),
        'Beta Recall':       round(report['3']['recall'], 4),
        'Macro F1':          round(res['f1_macro'], 4),
        'Weighted F1':       round(res['f1_weighted'], 4),
        'Accuracy':          round(report['accuracy'], 4),
    })

summary = pd.DataFrame(summary_rows).sort_values('SC Recall ★', ascending=False)
print('=== FINAL MODEL COMPARISON ===')
print(summary.to_string(index=False))

best_row = summary.iloc[0]
print(f'\n✓ Recommended model: {best_row["Model"]}')
print(f'  Silent carrier recall: {best_row["SC Recall ★"]}')
print(f'  Macro F1: {best_row["Macro F1"]}')

# --- CELL ---
def predict_thalassemia_risk(rbc, hgb, mcv, mch, mchc, rdw, sex=None):
    """
    Thalassemia screening prototype.
    
    Parameters
    ----------
    rbc, hgb, mcv, mch, mchc, rdw : float  — CBC values
    sex : int or None               — 0=female, 1=male (optional)

    Returns
    -------
    dict with predicted class, class probabilities, risk score,
    binary carrier flag, and top feature contributions.
    """
    # Build raw feature row
    raw = {'RBC': rbc, 'HGB': hgb, 'MCV': mcv, 'MCH': mch, 'MCHC': mchc, 'RDW': rdw}
    row = pd.DataFrame([raw])
    row = add_clinical_indices(row)
    row_vals = row[FEATURE_COLS].values

    # Scale
    row_sc = scaler.transform(row_vals)

    # Multi-class prediction
    best_model = fitted_models[BEST_MODEL_NAME]
    pred_class = best_model.predict(row_sc)[0]
    pred_probs = best_model.predict_proba(row_sc)[0]

    # Ordinal risk score (higher = more severe)
    ordinal_pred = ordinal_model.predict(row_sc)[0]

    # Binary carrier
    carrier_prob = bin_lr.predict_proba(row_sc)[0][1]
    is_carrier   = carrier_prob >= 0.50

    # Confidence: flag for review if top two probs are close
    sorted_probs = np.sort(pred_probs)[::-1]
    uncertain    = (sorted_probs[0] - sorted_probs[1]) < 0.15

    result = {
        'predicted_class':    LABEL_MAP[pred_class],
        'confidence':         round(float(sorted_probs[0]), 4),
        'class_probabilities': {LABEL_MAP[i]: round(float(p), 4) for i, p in enumerate(pred_probs)},
        'ordinal_severity':   ORDINAL_NAMES[int(ordinal_pred)],
        'carrier_probability': round(float(carrier_prob), 4),
        'is_carrier':          bool(is_carrier),
        'flag_for_review':     bool(uncertain),
        'mentzer_index':       round(float(mcv / rbc), 3),
        'mentzer_interpretation': 'Suggests thalassemia' if (mcv / rbc) < 13 else 'Suggests IDA or normal',
    }
    return result


import json

cases = [
    dict(label='Normal',         rbc=4.86, hgb=14.6, mcv=90.0, mch=30.1, mchc=33.4, rdw=13.5),
    dict(label='Silent Carrier', rbc=4.33, hgb=11.0, mcv=78.3, mch=25.3, mchc=32.4, rdw=14.2),
    dict(label='Alpha Trait',    rbc=4.74, hgb=12.5, mcv=79.1, mch=26.3, mchc=33.3, rdw=14.2),
    dict(label='Beta Trait',     rbc=5.30, hgb=8.7,  mcv=49.0, mch=16.3, mchc=33.5, rdw=18.2),
]

for case in cases:
    true_label = case.pop('label')
    result = predict_thalassemia_risk(**case)
    print(f'--- True: {true_label} ---')
    print(f'  Predicted:         {result["predicted_class"]}  (confidence: {result["confidence"]})')
    print(f'  Ordinal severity:  {result["ordinal_severity"]}')
    print(f'  Carrier prob:      {result["carrier_probability"]}')
    print(f'  Flag for review:   {result["flag_for_review"]}')
    print(f'  Mentzer index:     {result["mentzer_index"]} → {result["mentzer_interpretation"]}')
    print()

