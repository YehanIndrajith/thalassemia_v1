<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class PredictionController extends Controller
{
    public function index()
    {
        return view('prediction.index');
    }

    public function predict(Request $request)
    {
        $validated = $request->validate([
            'hb' => 'required|numeric',
            'mcv' => 'required|numeric',
            'mch' => 'required|numeric',
            'mchc' => 'required|numeric',
            'rbc' => 'required|numeric',
            'rdw' => 'required|numeric',
            'gender' => 'nullable|string',
            'age' => 'nullable|numeric',
        ]);

        // Path to the python script
        $scriptPath = base_path('ml_model/predict.py');

        // We use 'py' or 'python' depending on the environment. We detected 'py' earlier.
        $process = new Process(['py', $scriptPath]);
        
        // Pass the json payload to standard input
        $process->setInput(json_encode($validated));
        $process->run();

        if (!$process->isSuccessful()) {
            return back()->withErrors(['ml_error' => 'Model prediction failed: ' . $process->getErrorOutput()])->withInput();
        }

        $output = $process->getOutput();
        $result = json_decode($output, true);

        if (json_last_error() !== JSON_ERROR_NONE || isset($result['error'])) {
            $errorMsg = isset($result['error']) ? $result['error'] : 'Invalid JSON from python script.';
            return back()->withErrors(['ml_error' => 'Prediction Error: ' . $errorMsg])->withInput();
        }

        return view('prediction.index', [
            'result' => $result,
            'input' => $validated
        ]);
    }
}
