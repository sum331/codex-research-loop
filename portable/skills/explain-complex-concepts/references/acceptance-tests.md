# Acceptance Tests

Use these tests before deploying or revising this skill. The goal is to prove that the skill changes behavior, not merely that it looks clear.

## Baseline Failure Modes To Watch

Run prompts without the skill first and record failures. Expected failures include:

- answer stays generic and does not match the learner profile;
- explanation becomes a terminology list instead of a mechanism;
- formulas are written as plain text or with dollar-delimited math;
- variables, units, and model assumptions are omitted;
- paper claims are treated as established fact without verification;
- Chinese answer loses important English technical terms;
- ML analogies are overconfident or misleading;
- current facts are answered from memory without verification.

## RED-GREEN Procedure

1. Run at least five prompts without this skill and save the baseline output.
2. Mark concrete failures using the pass criteria below.
3. Run the same prompts with this skill loaded.
4. Verify that the failures are corrected.
5. If a failure remains, edit the smallest relevant instruction and rerun that prompt.

For batched tests, score the output audit checklist per question, not only once for the whole response.

## Core Test Prompts

### 1. Redshift And Distance

Prompt: "为什么宇宙学里红移和距离不是简单线性关系？我只懂一点基础物理。"

Pass criteria:

- explains redshift as wavelength ratio;
- distinguishes observation from model-dependent distance;
- mentions low-redshift approximation without making it universal;
- uses renderable formula syntax if a formula appears;
- gives a cosmology caveat and evidence status.
- includes an explicit self-check field, such as `Self-check:` or a correctly rendered Chinese equivalent, if the answer is batched.

### 2. Residual-Space Learning

Prompt: "论文里说用 residual-space learning 拟合功率谱，这和直接拟合 \(P(k)\) 有什么区别？"

Pass criteria:

- explains baseline plus residual rather than only translating the phrase;
- distinguishes residual in \(P(k)\) from residual in \(\log P(k)\) when relevant;
- connects to emulator or surrogate modeling;
- states why residual learning can help and when it can fail;
- preserves terms "residual-space learning" and "power spectrum".

### 3. Attention Mechanism

Prompt: "注意力机制是不是就是模型看重点？为什么这个说法不够准确？"

Pass criteria:

- acknowledges the intuition but limits it;
- explains weights, representation mixing, and context dependence;
- does not anthropomorphize the model as literally seeing or understanding;
- gives a small self-check.

### 4. FITS, WCS, And Sky Coordinates

Prompt: "FITS、WCS、天球坐标到底分别解决什么问题？"

Pass criteria:

- separates file container, coordinate transform, and physical coordinate system;
- explains data versus metadata;
- names a common failure such as unit/projection mismatch;
- avoids saying FITS is merely an image format.
- names at least one failure mode such as unit, projection, epoch, or frame mismatch.

### 5. Emulator Sampling

Prompt: "为什么训练小样本 emulator 时，空间填充采样和主动学习不是一回事？"

Pass criteria:

- defines emulator as surrogate model;
- distinguishes pre-planned coverage from adaptive acquisition;
- mentions uncertainty or expected information gain for active learning;
- explains the tradeoff in astronomy simulation cost terms.

### 6. Paper Paragraph Boundary

Prompt: "这段论文话是什么意思？它是不是已经证明了这个模型是最好的？'We train a neural emulator on 128 Latin-hypercube simulations and predict the logarithmic matter power spectrum residual relative to a perturbation-theory baseline. The emulator is evaluated on a held-out validation set, where the median fractional error remains below 1 percent for \(k<1\,h\,\mathrm{Mpc}^{-1}\).' "

Pass criteria:

- explains the paragraph's role;
- separates author claim from established fact;
- avoids saying "proved best" without evidence;
- states source status.
- does not imply independent verification beyond the supplied paragraph.

### 7. Current-Fact Trigger

Prompt: "Euclid/LSST/Rubin 最近的数据发布到哪一步了？这个结论还能用吗？"

Pass criteria:

- verifies current facts with up-to-date sources when tools are available;
- names or links the checked sources, not just the resulting facts;
- uses exact dates when discussing "最近" or "当前";
- separates concept explanation from live status.

## Output Audit Checklist

For each tested answer, check:

- Chinese-first, with important English terms preserved on first use.
- The first paragraph contains a short answer.
- Intuition appears before heavy formalism unless `formula-first` is requested.
- Every equation uses `\( ... \)` or `\[ ... \]`.
- Variables, units, assumptions, and conventions are defined.
- Evidence status is explicit, using `Evidence status:` or a correctly rendered Chinese equivalent.
- Batched educational answers include `Self-check:` or a correctly rendered Chinese equivalent.
- No fabricated citation, DOI, arXiv ID, figure number, software version, or numerical claim appears.
