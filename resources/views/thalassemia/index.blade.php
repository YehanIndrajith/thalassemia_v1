@extends('layouts.app')

@section('title', 'THALAI - Thalassemia Risk Screening')

@section('content')
    {{-- Section 1: Title & Description --}}
    <div class="card">
        <h1>THALAI</h1>
        <p class="muted">
            This prototype predicts thalassemia genotype risk using Complete Blood Count (CBC) parameters and a trained machine learning model.
        </p>
        <p class="muted">
            This system is intended for <strong>screening support only</strong>.
        </p>
        <div class="disclaimer">
            <strong>For screening and research purposes only.</strong> This tool does not replace clinical diagnosis.
        </div>
    </div>

    {{-- Section 2: CBC Input Fields --}}
    <div class="card">
        <h2>CBC Input</h2>
        <p class="muted">Enter the Complete Blood Count parameters. All CBC fields are required.</p>

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
                    <input type="number" step="0.1" name="hemoglobin" id="hemoglobin" value="{{ old('hemoglobin') }}" placeholder="e.g. 10.8" required>
                </div>
                <div class="form-group">
                    <label for="mcv">MCV — fL</label>
                    <input type="number" step="0.1" name="mcv" id="mcv" value="{{ old('mcv') }}" placeholder="e.g. 64" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="mch">MCH — pg</label>
                    <input type="number" step="0.1" name="mch" id="mch" value="{{ old('mch') }}" placeholder="e.g. 20" required>
                </div>
                <div class="form-group">
                    <label for="rbc">RBC — ×10¹²/L</label>
                    <input type="number" step="0.01" name="rbc" id="rbc" value="{{ old('rbc') }}" placeholder="e.g. 5.8" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="rdw">RDW — %</label>
                    <input type="number" step="0.1" name="rdw" id="rdw" value="{{ old('rdw') }}" placeholder="e.g. 16" required>
                </div>
                <div class="form-group">
                    <label for="mchc">MCHC — g/dL</label>
                    <input type="number" step="0.1" name="mchc" id="mchc" value="{{ old('mchc') }}" placeholder="e.g. 33" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="gender">Gender (optional)</label>
                    <select name="gender" id="gender">
                        <option value="">— Select —</option>
                        <option value="male" {{ old('gender') === 'male' ? 'selected' : '' }}>Male</option>
                        <option value="female" {{ old('gender') === 'female' ? 'selected' : '' }}>Female</option>
                        <option value="other" {{ old('gender') === 'other' ? 'selected' : '' }}>Other</option>
                    </select>
                </div>
            <div class="form-group" style="max-width: 200px;">
                <label for="age">Age (optional)</label>
                <input type="number" name="age" id="age" value="{{ old('age') }}" placeholder="Years" min="0" max="120">
            </div>
            <div style="margin-top: 1.25rem;">
                <button type="submit" class="btn">Predict Risk</button>
            </div>
        </form>
    </div>
@endsection
