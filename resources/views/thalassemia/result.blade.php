@extends('layouts.app')

@section('title', 'Prediction Result - THALAI')

@section('content')
    {{-- Section 1: Title & Description (short) --}}
    <div class="card">
        <h1>THALAI</h1>
        <p class="muted">Thalassemia genotype risk prediction from CBC parameters. For screening and research purposes only.</p>
        <div class="disclaimer">
            <strong>For screening and research purposes only.</strong> This tool does not replace clinical diagnosis.
        </div>
    </div>

    {{-- Section 3: Prediction Output --}}
    <div class="card">
        <h2>Prediction Result</h2>

        {{-- 1. Predicted Risk Category --}}
        <p class="muted" style="margin-bottom: 0.25rem;">Predicted Risk Category:</p>
        <p class="result-category">{{ $predicted_category }}</p>

        {{-- 2. Prediction Probability --}}
        <p class="muted" style="margin-top: 1rem; margin-bottom: 0.25rem;">Prediction Confidence: <strong>{{ $confidence }}%</strong></p>
        <p class="muted" style="margin-bottom: 0.5rem;">Class Probabilities:</p>
        <table class="probs">
            <thead>
                <tr>
                    <th>Class</th>
                    <th>Probability</th>
                </tr>
            </thead>
            <tbody>
                @php
                    $labels = [
                        'normal' => 'Normal',
                        'silent_carrier' => 'Silent Carrier',
                        'alpha_trait' => 'Alpha Trait',
                        'beta_trait' => 'Beta Trait',
                    ];
                @endphp
                @foreach ($probabilities as $key => $prob)
                    <tr class="{{ $key === $predicted_key ? 'highest' : '' }}">
                        <td>{{ $labels[$key] ?? $key }}</td>
                        <td>{{ (int) round($prob * 100) }}%</td>
                    </tr>
                @endforeach
            </tbody>
        </table>

        {{-- 3. Ordinal Severity & Carrier Status --}}
        <p class="muted" style="margin-top: 1.25rem; margin-bottom: 0.35rem;">Additional Metrics:</p>
        <ul class="contributions">
            <li><strong>Ordinal severity:</strong> {{ $ordinal_severity }}</li>
            <li><strong>Carrier prob:</strong> {{ round($carrier_probability * 100, 1) }}% ({{ $is_carrier ? 'Carrier' : 'Not a carrier' }})</li>
            <li>
                <strong>Flag for review:</strong> 
                @if($flag_for_review)
                    <span style="color: #ef4444; font-weight: bold;">True</span> (Top predictions are close)
                @else
                    False
                @endif
            </li>
            <li><strong>Mentzer index:</strong> {{ $mentzer_index }} &rarr; {{ $mentzer_interpretation }}</li>
        </ul>

        <p class="muted" style="margin-top: 1rem; font-size: 0.9rem;">
            This tool provides screening support only and does not replace clinical diagnosis.
        </p>

        <div class="back-link">
            <a href="{{ route('thalassemia.index') }}">← Enter new CBC values</a>
        </div>
    </div>
@endsection
