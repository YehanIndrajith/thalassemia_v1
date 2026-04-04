# THALAI — Thalassemia Risk Screening Prototype

A Laravel-based prototype that predicts thalassemia genotype risk from Complete Blood Count (CBC) parameters.

**For screening and research purposes only.** This tool does not replace clinical diagnosis.

## Requirements

- PHP 8.2+
- Composer
- Laragon (recommended on Windows) or any PHP stack

## Setup

1. **Install dependencies** (from project root, in a terminal where PHP/Composer are in PATH — e.g. Laragon terminal):

   ```bash
   composer install
   ```

2. **Environment**:

   ```bash
   copy .env.example .env
   php artisan key:generate
   ```

3. **Run the app**:

   - **Option A:** Laragon: add `thalassemia` as a project and open `http://thalassemia.test` (point document root to `public`).
   - **Option B:** Built-in server: `php artisan serve` then open `http://localhost:8000`.

## Usage

1. Open the app in the browser.
2. Enter CBC values: **Hemoglobin (Hb)**, **MCV**, **MCH**, **RBC**, **RDW**. Optionally **Gender** and **Age**.
3. Click **Predict Risk**.
4. View: predicted risk category, class probabilities, key contributing features, and analytical risk score.

## Example

- **Input:** Hb = 10.8, MCV = 64, MCH = 20, RBC = 5.8, RDW = 16  
- **Output:** e.g. β-Thalassemia Trait, with probabilities and feature contributions.

## Replacing with a trained model

The prediction logic in `app/Http/Controllers/ThalassemiaController.php` is currently **rule-based** (Mentzer-like indices and heuristics). To use a real trained model:

1. Integrate your model (e.g. PHP extension, Python subprocess, or API).
2. Replace `runPrediction()` / `computeProbabilities()` with model inference.
3. Use SHAP or your model’s feature importance for **Key Contributing Features**.

## License

MIT
