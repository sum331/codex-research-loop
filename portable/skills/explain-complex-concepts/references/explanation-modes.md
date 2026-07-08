# Explanation Modes

Choose one mode from the user's wording. If no mode is specified, use `deep-intuition`.

| Mode | Use when | Output shape |
| --- | --- | --- |
| `quick-intuition` | user asks "简单说", "一句话", or wants a quick check | short answer, intuition, one caveat, evidence status |
| `deep-intuition` | default for complex professional questions | full explanation contract from `SKILL.md` |
| `formula-first` | user explicitly asks for derivation, equations, or mathematical rigor | assumptions, formula, variable definitions, interpretation, caveats |
| `paper-paragraph` | user provides a paper sentence, paragraph, figure caption, or method section | translate meaning, unpack terms, identify claim, explain method, mark source status |
| `code-data-context` | user asks about data formats, pipelines, arrays, coordinates, APIs, or model implementation | conceptual map, data object roles, minimal pseudocode if helpful, traps |
| `comparison` | user asks "A 和 B 有什么区别" | shared goal, key distinction, example, when each applies, misconception |

## Mode Templates

### `quick-intuition`

Use 3 to 5 short paragraphs:

1. One-sentence answer.
2. Concrete picture.
3. One formal caveat or equation if needed.
4. Evidence status.

### `deep-intuition`

Use the default explanation contract from `SKILL.md`. Keep each section compact; do not turn every answer into a textbook chapter.

### `formula-first`

Use this sequence:

1. State assumptions and convention.
2. Present the formula with renderable LaTeX.
3. Define symbols and units.
4. Interpret each term.
5. Give one numerical or physical intuition if possible.
6. State limitations.

Example source style:

\[
D_{\mathrm{L}}=(1+z)D_{\mathrm{M}}
\]

Here \(D_{\mathrm{L}}\) is luminosity distance, \(z\) is redshift, and \(D_{\mathrm{M}}\) is transverse comoving distance in the chosen cosmological model.

### `paper-paragraph`

Use this sequence:

1. Say what the paragraph is trying to do in the paper.
2. Explain each important term.
3. Distinguish data, method, assumption, and conclusion.
4. Explain the key equation or figure reference if present.
5. Mark what is claimed by the paper versus what is generally established.

### `code-data-context`

Use this sequence:

1. Identify the objects involved, such as array, header, coordinate frame, model input, or target.
2. Explain what each object represents.
3. Describe transformations between objects.
4. State failure modes, such as unit mismatch, coordinate convention mismatch, leakage, or extrapolation.
5. Add minimal pseudocode only if it clarifies the concept.

### `comparison`

Use this sequence:

1. Start with the one-line distinction.
2. Explain the shared problem both concepts address.
3. Give a table with 3 to 5 differences.
4. Give one astronomy or ML example.
5. State the common misconception.
