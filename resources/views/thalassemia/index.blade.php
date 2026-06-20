@extends('layouts.app')

@section('title', 'THALAI - Thalassemia Genotype Risk Screening')

@section('content')
    {{-- Title & Header --}}
    <div class="card" style="margin-bottom: 1.5rem; text-align: center; padding: 2rem 1.5rem;">
        <span style="font-size: 0.72rem; background: rgba(99, 102, 241, 0.08); color: var(--accent); padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem; display: inline-block; border: 1px solid rgba(99, 102, 241, 0.15);">
            Machine Learning Diagnostics
        </span>
        <h1 style="display: block; margin-bottom: 0.5rem;">THALAI</h1>
        <p class="muted" style="max-width: 500px; margin: 0 auto; line-height: 1.5; font-size: 0.88rem;">
            A screening support system predicting thalassemia genotype risk using standard Complete Blood Count (CBC) parameters.
        </p>
        <div class="disclaimer" style="justify-content: center; margin-top: 1.25rem; max-width: 480px; margin-left: auto; margin-right: auto;">
            <span>⚠️</span>
            <strong>For screening & research only.</strong> Does not replace clinical diagnosis.
        </div>
    </div>

    {{-- CBC Form --}}
    <div class="card" style="padding: 1.75rem;">
        <h2 style="margin-bottom: 0.25rem; font-size: 1.15rem;">CBC Parameters</h2>
        <p class="muted" style="margin-bottom: 1.25rem; font-size: 0.85rem;">All fields below are required to run prediction.</p>

        @if ($errors->any())
            <ul class="error-list">
                @foreach ($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        @endif

        <form action="{{ route('thalassemia.predict') }}" method="POST">
            @csrf
            <div class="form-row">
                <div class="form-group">
                    <label for="hemoglobin">Hemoglobin (Hb) — g/dL</label>
                    <input type="number" step="0.01" name="hemoglobin" id="hemoglobin" value="{{ old('hemoglobin') }}" placeholder="e.g. 10.8" required>
                </div>
                <div class="form-group">
                    <label for="mcv">MCV — fL</label>
                    <input type="number" step="0.01" name="mcv" id="mcv" value="{{ old('mcv') }}" placeholder="e.g. 64.0" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="mch">MCH — pg</label>
                    <input type="number" step="0.01" name="mch" id="mch" value="{{ old('mch') }}" placeholder="e.g. 20.0" required>
                </div>
                <div class="form-group">
                    <label for="rbc">RBC — ×10¹²/L</label>
                    <input type="number" step="0.01" name="rbc" id="rbc" value="{{ old('rbc') }}" placeholder="e.g. 5.80" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="rdw">RDW — %</label>
                    <input type="number" step="0.01" name="rdw" id="rdw" value="{{ old('rdw') }}" placeholder="e.g. 16.0" required>
                </div>
                <div class="form-group">
                    <label for="mchc">MCHC — g/dL</label>
                    <input type="number" step="0.01" name="mchc" id="mchc" value="{{ old('mchc') }}" placeholder="e.g. 33.0" required>
                </div>
            </div>
            
            <div style="border-top: 1px solid var(--border); margin: 0.75rem 0 1.25rem 0; padding-top: 1rem;">
                <h3 style="font-size: 0.95rem; color: #ffffff; margin-bottom: 0.75rem; font-weight: 500; font-family: var(--font-heading);">
                    Demographics (Optional)
                </h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="gender">Gender</label>
                        <select name="gender" id="gender">
                            <option value="">Select Gender</option>
                            <option value="male" {{ old('gender') === 'male' ? 'selected' : '' }}>Male</option>
                            <option value="female" {{ old('gender') === 'female' ? 'selected' : '' }}>Female</option>
                            <option value="other" {{ old('gender') === 'other' ? 'selected' : '' }}>Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="age">Age</label>
                        <input type="number" name="age" id="age" value="{{ old('age') }}" placeholder="Years" min="0" max="120">
                    </div>
                </div>
            </div>

            <div style="text-align: center; margin-top: 0.5rem;">
                <button type="submit" class="btn" style="width: 100%; padding: 0.75rem 1.5rem;">
                    Run Diagnostic Prediction
                </button>
            </div>
        </form>
    </div>
@endsection
