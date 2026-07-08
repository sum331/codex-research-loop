# Astronomy And ML Bridge

Use this file to connect astronomy, physics, statistics, and machine learning without collapsing one field into another.

## Common Bridge Patterns

| Concept | Astronomy meaning | ML/statistics bridge | Trap to avoid |
| --- | --- | --- | --- |
| FITS | container for arrays plus metadata headers | like data plus schema, but with astronomy-specific conventions | saying FITS is "just an image" |
| WCS | mapping between pixel coordinates and sky coordinates | a transformation layer between index space and physical coordinate space | ignoring projection and units |
| Redshift | observed wavelength stretch tied to expansion, velocity, or gravity by context | an observed feature that maps to model-dependent distance or epoch | treating redshift as a direct distance ruler |
| Power spectrum | variance or clustering strength as a function of scale | target function over \(k\), often modeled or emulated | calling it just a Fourier transform |
| Emulator | fast surrogate for expensive simulations | supervised model approximating a simulator response | treating emulator predictions as simulation truth |
| Residual learning | model learns a correction to a baseline | learn \(r(x)=y_{\mathrm{truth}}(x)-y_{\mathrm{base}}(x)\) or a transformed residual | forgetting residual depends on baseline quality |
| Active learning | choose new samples based on model uncertainty or expected gain | adaptive experimental design | confusing it with any space-filling design |
| Selection function | probability that an object enters the observed sample | observation process or missingness mechanism | treating observed data as unbiased truth |

## Formula Anchors

Use formulas only when they clarify the concept and define every symbol.

### Redshift

\[
1+z=\frac{\lambda_{\mathrm{obs}}}{\lambda_{\mathrm{emit}}}
\]

Here \(z\) is redshift, \(\lambda_{\mathrm{obs}}\) is observed wavelength, and \(\lambda_{\mathrm{emit}}\) is emitted or rest-frame wavelength. This definition alone does not specify a unique physical distance without a model.

### Power Spectrum

\[
\langle \delta(\mathbf{k})\delta^{*}(\mathbf{k}') \rangle
=
(2\pi)^3\delta_{\mathrm{D}}(\mathbf{k}-\mathbf{k}')P(k)
\]

Here \(\delta(\mathbf{k})\) is the Fourier-space density contrast, \(\delta_{\mathrm{D}}\) is the Dirac delta distribution, and \(P(k)\) is the power spectrum as a function of wavenumber \(k\). State the Fourier convention if it matters.

### Residual Learning

\[
r(x)=y_{\mathrm{truth}}(x)-y_{\mathrm{base}}(x)
\]

Here \(x\) is the input condition, \(y_{\mathrm{truth}}\) is the target, \(y_{\mathrm{base}}\) is a baseline model, and \(r(x)\) is the residual to learn. In log-space power spectrum work, define whether the residual is additive in \(P(k)\) or in \(\log P(k)\).

## Safe Analogy Rules

Use analogies to open the door, then return to the exact object.

Good pattern:

1. "可以把它暂时想成..."
2. "但严格说，它是..."
3. "这个类比会失效在..."

Examples:

- WCS is like a coordinate translator, but not a simple dictionary lookup because projections, distortions, epochs, and units matter.
- An emulator is like a fast approximation to a simulation, but it must carry uncertainty and can fail outside the training domain.
- A power spectrum is like asking "which spatial scales dominate variation", but the exact definition depends on the field, transform convention, and normalization.

## Astronomy Explanation Checklist

Before finalizing an astronomy-related explanation, check:

- Are units and coordinate frames named?
- Is the quantity observational, theoretical, simulated, or inferred?
- Is the statement model-dependent?
- Does the explanation distinguish data, metadata, calibration, and inference?
- If ML is involved, is the target, input, loss, uncertainty, and extrapolation risk clear?
