@extends('layouts.app')

@section('title', 'Prediction Result - THALAI')

@section('content')
    {{-- Header --}}
    <div class="card" style="margin-bottom: 1.25rem; display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.5rem;">
        <div>
            <h1 style="font-size: 1.5rem; margin-bottom: 0.15rem;">THALAI</h1>
            <p class="muted" style="font-size: 0.8rem;">Clinical Genotype Risk Report</p>
        </div>
        <div class="back-link">
            <a href="{{ route('thalassemia.index') }}">← New Screening</a>
        </div>
    </div>

    {{-- Section 3: Prediction Output --}}
    <div class="card" style="padding: 1.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem;">
            <div>
                <p class="muted" style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; margin-bottom: 0.25rem;">
                    Predicted Genotype
                </p>
                <p class="result-category" style="margin: 0; color: #ffffff; font-size: 1.65rem;">{{ $predicted_category }}</p>
            </div>
            <div style="text-align: right;">
                <p class="muted" style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; margin-bottom: 0.25rem;">
                    Confidence
                </p>
                <div style="display: flex; align-items: center; gap: 0.4rem; justify-content: flex-end;">
                    <span style="font-size: 1.5rem; font-weight: 700; color: var(--accent); font-family: var(--font-heading);">{{ $confidence }}%</span>
                    @if(isset($used_http) && $used_http)
                        <span class="shap-performance-badge" style="margin: 0;" title="Served in <50ms by preloaded HTTP daemon">⚡ Fast</span>
                    @else
                        <span class="shap-performance-badge slow" style="margin: 0;" title="Served in ~9s by standard CLI bootup. Run service.py to optimize.">⚠️ Slow</span>
                    @endif
                </div>
            </div>
        </div>

        {{-- Class Probabilities Table with Progress Bars --}}
        <h3 style="font-size: 0.95rem; color: #ffffff; margin-bottom: 0.5rem; font-weight: 500; font-family: var(--font-heading);">
            Genotype Probability Distribution
        </h3>
        <table class="probs" style="margin-bottom: 1.5rem;">
            <thead>
                <tr>
                    <th>Genotype</th>
                    <th style="text-align: right; padding-right: 0.85rem;">Probability</th>
                </tr>
            </thead>
            <tbody>
                @php
                    $labels = [
                        'normal' => 'Normal Genotype',
                        'silent_carrier' => 'Silent Carrier',
                        'alpha_trait' => 'Alpha Thalassemia Trait',
                        'beta_trait' => 'Beta Thalassemia Trait',
                    ];
                @endphp
                @foreach ($probabilities as $key => $prob)
                    <tr class="{{ $key === $predicted_key ? 'highest' : '' }}">
                        <td style="font-weight: {{ $key === $predicted_key ? '500' : '300' }};">
                            {{ $labels[$key] ?? $key }}
                        </td>
                        <td style="width: 55%; padding-right: 0;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; justify-content: flex-end;">
                                <div style="flex-grow: 1; max-width: 140px; height: 6px; background: rgba(255, 255, 255, 0.03); border-radius: 3px; overflow: hidden; position: relative;">
                                    <div style="height: 100%; width: {{ $prob * 100 }}%; background: {{ $key === $predicted_key ? 'var(--accent)' : 'rgba(255, 255, 255, 0.15)' }}; border-radius: 3px;"></div>
                                </div>
                                <span style="font-family: monospace; font-size: 0.85rem; width: 45px; text-align: right; display: inline-block;">
                                    {{ (int) round($prob * 100) }}%
                                </span>
                            </div>
                        </td>
                    </tr>
                @endforeach
            </tbody>
        </table>

        {{-- Grid of Additional Metrics --}}
        <h3 style="font-size: 0.95rem; color: #ffffff; margin-bottom: 0.75rem; font-weight: 500; font-family: var(--font-heading);">
            Diagnostic Metrics
        </h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1rem;">
                <p class="muted" style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.15rem;">
                    Mentzer Index
                </p>
                <p style="font-size: 1rem; font-weight: 600; color: #ffffff; margin-bottom: 0.1rem;">
                    {{ $mentzer_index }}
                </p>
                <p class="muted" style="font-size: 0.75rem; color: {{ $mentzer_index < 13 ? '#fb7185' : 'var(--muted)' }}">
                    {{ $mentzer_interpretation }}
                </p>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1rem;">
                <p class="muted" style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.15rem;">
                    Carrier Status
                </p>
                <p style="font-size: 1rem; font-weight: 600; color: #ffffff; margin-bottom: 0.1rem;">
                    {{ $is_carrier ? 'Carrier Flagged' : 'Normal / Low Risk' }}
                </p>
                <p class="muted" style="font-size: 0.75rem;">
                    Probability: {{ round($carrier_probability * 100, 1) }}%
                </p>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1rem;">
                <p class="muted" style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.15rem;">
                    Clinical Severity
                </p>
                <p style="font-size: 1rem; font-weight: 600; color: #ffffff; margin-bottom: 0.1rem;">
                    {{ $ordinal_severity }}
                </p>
                <p class="muted" style="font-size: 0.75rem;">
                    Genotype severity ranking
                </p>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1rem;">
                <p class="muted" style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.15rem;">
                    Review Required
                </p>
                @if($flag_for_review)
                    <p style="font-size: 1rem; font-weight: 600; color: #fb7185; margin-bottom: 0.1rem;">
                        ⚠️ Yes
                    </p>
                    <p class="muted" style="font-size: 0.75rem; color: #fb7185;">
                        Top predictions are close
                    </p>
                @else
                    <p style="font-size: 1rem; font-weight: 600; color: #34d399; margin-bottom: 0.1rem;">
                        ✓ No
                    </p>
                    <p class="muted" style="font-size: 0.75rem; color: #34d399;">
                        High prediction margin
                    </p>
                @endif
            </div>
        </div>
    </div>

    {{-- Section 4: Explainable AI (XAI) Model Interpretation --}}
    @if (!empty($shap_values))
        <div class="card" style="padding: 1.75rem;">
            <h2 style="color: #ffffff; font-size: 1.15rem; margin-top: 0; margin-bottom: 0.25rem;">
                Explainable AI (XAI) Model Interpretation
            </h2>
            <p class="muted" style="margin-bottom: 1.25rem; font-size: 0.85rem;">
                Quantitative analysis explaining parameter contributions to the predicted diagnosis.
            </p>

            {{-- Web-Native Interactive SHAP Diverging Bar Chart --}}
            @php
                $maxAbsShap = 0.0001;
                foreach ($shap_values as $val) {
                    if (abs($val) > $maxAbsShap) {
                        $maxAbsShap = abs($val);
                    }
                }
                // Sort by absolute influence descending so key factors appear first
                uasort($shap_values, function($a, $b) {
                    return abs($b) <=> abs($a);
                });
            @endphp

            <div class="shap-bars">
                <h3 style="margin-top: 0; margin-bottom: 0.35rem; font-size: 0.9rem; color: var(--text); font-weight: 500; font-family: var(--font-heading);">
                    Feature Contribution Details (SHAP values)
                </h3>
                <p class="muted" style="margin-top: 0; margin-bottom: 1.25rem; font-size: 0.8rem;">
                    Parameters extending <span style="color: #fb7185; font-weight: 500;">right (red)</span> pushed towards <strong>{{ $predicted_category }}</strong>. Parameters extending <span style="color: #60a5fa; font-weight: 500;">left (blue)</span> pulled away.
                </p>

                @foreach ($shap_values as $feat => $val)
                    @php
                        $percent = (abs($val) / $maxAbsShap) * 100;
                        $featLabel = $feat;
                        if ($feat === 'EnglandFraser') $featLabel = 'England & Fraser';
                        if ($feat === 'ShineLal') $featLabel = 'Shine & Lal';
                        if ($feat === 'GreenKing') $featLabel = 'Green & King';
                        if ($feat === 'RDWI') $featLabel = 'RDW Index (RDWI)';
                        if ($feat === 'MCHC_MCH_ratio') $featLabel = 'MCHC/MCH Ratio';
                        if ($feat === 'HGB_RBC_ratio') $featLabel = 'HGB/RBC Ratio';
                    @endphp
                    <div class="shap-bar-row" title="Feature: {{ $featLabel }}, SHAP value: {{ number_format($val, 6) }}">
                        <div class="shap-bar-label">{{ $featLabel }}</div>
                        <div class="shap-bar-track">
                            <div class="shap-bar-fill-left-container">
                                @if ($val < 0)
                                    <div class="shap-bar-fill negative" style="width: {{ $percent }}%;"></div>
                                @endif
                            </div>
                            <div class="shap-bar-center-divider"></div>
                            <div class="shap-bar-fill-right-container">
                                @if ($val > 0)
                                    <div class="shap-bar-fill positive" style="width: {{ $percent }}%;"></div>
                                @endif
                            </div>
                        </div>
                        <div class="shap-bar-value {{ $val >= 0 ? 'pos' : 'neg' }}">
                            {{ $val >= 0 ? '+' : '' }}{{ number_format($val, 4) }}
                        </div>
                    </div>
                @endforeach

                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--muted); margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.65rem;">
                    <span>← Pulls Away (Negative)</span>
                    <span>Average baseline: {{ number_format($base_value * 100, 1) }}%</span>
                    <span>Pushes Toward (Positive) →</span>
                </div>
            </div>

            {{-- Local SHAP Waterfall Image --}}
            @if ($waterfall_image)
                <div style="margin-top: 1.75rem;">
                    <h3 style="font-size: 0.95rem; color: #ffffff; margin-bottom: 0.25rem; font-weight: 500; font-family: var(--font-heading);">
                        Patient SHAP Waterfall Chart
                    </h3>
                    <p class="muted" style="margin-top: 0; margin-bottom: 0.75rem; font-size: 0.8rem;">
                        Waterfall trajectory mapping baseline expectation shift to final predicted probability.
                    </p>
                    <div class="xai-image-container">
                        <img src="{{ $waterfall_image }}" alt="Patient SHAP Waterfall Plot" class="xai-image">
                    </div>
                </div>
            @endif

            {{-- Global SHAP Tabbed Beeswarm Plots --}}
            <div style="margin-top: 2rem; border-top: 1px solid var(--border); padding-top: 1.5rem;">
                <h3 style="font-size: 0.95rem; color: #ffffff; margin-bottom: 0.25rem; font-weight: 500; font-family: var(--font-heading);">
                    Global Model Logic (Beeswarm Plots)
                </h3>
                <p class="muted" style="margin-top: 0; margin-bottom: 1rem; font-size: 0.8rem;">
                    Select a genotype to view the SHAP beeswarm plot mapping feature values to impact across the entire database cohort.
                </p>
                <div class="tabs-container">
                    <div class="tabs-nav">
                        <button class="tab-btn active" onclick="openTab(event, 'tab-normal')">Normal</button>
                        <button class="tab-btn" onclick="openTab(event, 'tab-silent')">Silent Carrier</button>
                        <button class="tab-btn" onclick="openTab(event, 'tab-alpha')">Alpha Trait</button>
                        <button class="tab-btn" onclick="openTab(event, 'tab-beta')">Beta Trait</button>
                        <button class="tab-btn" onclick="openTab(event, 'tab-importance')">Importance</button>
                    </div>
                    
                    <div id="tab-normal" class="tab-content active">
                        <div class="xai-image-container">
                            <img src="/images/shap_beeswarm_Normal.png" alt="SHAP Beeswarm - Normal" class="xai-image">
                        </div>
                    </div>
                    
                    <div id="tab-silent" class="tab-content">
                        <div class="xai-image-container">
                            <img src="/images/shap_beeswarm_Silent_Carrier.png" alt="SHAP Beeswarm - Silent Carrier" class="xai-image">
                        </div>
                    </div>
                    
                    <div id="tab-alpha" class="tab-content">
                        <div class="xai-image-container">
                            <img src="/images/shap_beeswarm_Alpha_Trait.png" alt="SHAP Beeswarm - Alpha Trait" class="xai-image">
                        </div>
                    </div>
                    
                    <div id="tab-beta" class="tab-content">
                        <div class="xai-image-container">
                            <img src="/images/shap_beeswarm_Beta_Trait.png" alt="SHAP Beeswarm - Beta Trait" class="xai-image">
                        </div>
                    </div>
                    
                    <div id="tab-importance" class="tab-content">
                        <div class="xai-image-container">
                            <img src="/images/shap_global_bar.png" alt="Global Feature Importance" class="xai-image">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    @endif

    <script>
        function openTab(evt, tabId) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].classList.remove("active");
            }
            tablinks = document.getElementsByClassName("tab-btn");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].classList.remove("active");
            }
            document.getElementById(tabId).classList.add("active");
            evt.currentTarget.classList.add("active");
        }
    </script>
@endsection
