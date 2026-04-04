<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\View\View;
use Illuminate\Http\RedirectResponse;

class ThalassemiaController extends Controller
{
    private const CATEGORIES = [
        'normal' => 'Normal',
        'silent_carrier' => 'Silent Carrier',
        'alpha_trait' => 'α-Thalassemia Trait',
        'beta_trait' => 'β-Thalassemia Trait',
    ];

    /**
     * Show the THALAI prototype form.
     */
    public function index(): View
    {
        return view('thalassemia.index');
    }

    /**
     * Run prediction and return result (rule-based prototype; replace with trained model later).
     */
    public function predict(Request $request): View|RedirectResponse
    {
        $validated = $request->validate([
            'hemoglobin' => 'required|numeric|min:0',
            'mcv' => 'required|numeric|min:0',
            'mch' => 'required|numeric|min:0',
            'mchc' => 'required|numeric|min:0',
            'rbc' => 'required|numeric|min:0',
            'rdw' => 'required|numeric|min:0',
            'gender' => 'nullable|in:male,female,other',
            'age' => 'nullable|integer|min:0|max:150',
        ], [
            'hemoglobin.required' => 'Hemoglobin (Hb) is required.',
            'mcv.required' => 'MCV is required.',
            'mch.required' => 'MCH is required.',
            'mchc.required' => 'MCHC is required.',
            'rbc.required' => 'RBC is required.',
            'rdw.required' => 'RDW is required.',
        ]);

        $result = $this->runPrediction($validated);
        $result['inputs'] = $validated;

        return view('thalassemia.result', $result);
    }

    /**
     * Call the trained Python ML model via CLI.
     */
    private function runPrediction(array $input): array
    {
        $scriptPath = base_path('ml_model/predict.py');
        $pythonExec = 'C:\\Users\\ASUS\\AppData\\Local\\Programs\\Python\\Launcher\\py.exe';
        $process = new \Symfony\Component\Process\Process([$pythonExec, $scriptPath]);
        
        // The ML script expects 'hb', 'mcv', 'mch', 'mchc', 'rbc', 'rdw'
        $payload = json_encode([
            'hb' => (float) $input['hemoglobin'],
            'mcv' => (float) $input['mcv'],
            'mch' => (float) $input['mch'],
            'mchc' => (float) $input['mchc'],
            'rbc' => (float) $input['rbc'],
            'rdw' => (float) $input['rdw'],
            'gender' => $input['gender'] ?? '',
            'age' => $input['age'] ?? 0,
        ]);
        
        $process->setInput($payload);
        $process->run();

        if (!$process->isSuccessful()) {
            // Fallback gracefully or bubble up error
            throw new \Exception('ML Model failed: ' . $process->getErrorOutput());
        }

        $output = $process->getOutput();
        $mlResult = json_decode($output, true);

        if (json_last_error() !== JSON_ERROR_NONE || isset($mlResult['error'])) {
            throw new \Exception('Invalid response from ML script: ' . ($mlResult['error'] ?? 'Unknown Error'));
        }

        // Map ML output to Blade view variables
        $probMap = [
            'normal' => ($mlResult['class_probabilities']['Normal'] ?? 0),
            'silent_carrier' => ($mlResult['class_probabilities']['Silent Carrier'] ?? 0),
            'alpha_trait' => ($mlResult['class_probabilities']['Alpha Trait'] ?? 0),
            'beta_trait' => ($mlResult['class_probabilities']['Beta Trait'] ?? 0),
        ];

        // Find the key with the highest prob
        $predictedKey = array_keys(self::CATEGORIES)[array_search($mlResult['predicted_class'], self::CATEGORIES)] ?? 'normal';

        return [
            'predicted_category' => $mlResult['predicted_class'] ?? 'Unknown',
            'predicted_key' => $predictedKey,
            'confidence' => (float) ($mlResult['confidence'] ?? 0),
            'probabilities' => $probMap,
            'ordinal_severity' => $mlResult['ordinal_severity'] ?? 'Unknown',
            'carrier_probability' => (float) ($mlResult['carrier_probability'] ?? 0),
            'is_carrier' => (bool) ($mlResult['is_carrier'] ?? false),
            'flag_for_review' => (bool) ($mlResult['flag_for_review'] ?? false),
            'mentzer_index' => (float) ($mlResult['mentzer_index'] ?? 0),
            'mentzer_interpretation' => $mlResult['mentzer_interpretation'] ?? '',
        ];
    }
}
