# Evidence Policy

## Claim Types

Classify claims before explaining them:

| Claim type | Examples | Required handling |
| --- | --- | --- |
| Stable background | definitions of redshift, FITS as a file format, basic likelihood meaning | explain directly; cite only if user asks |
| Model-dependent theory | cosmological distance, growth of structure, power spectrum convention | state assumptions and conventions |
| User-provided source | a pasted paper paragraph, figure caption, equation, or abstract | say the explanation is based on the provided source |
| Current or versioned fact | latest data release, current mission status, package API, software version | verify with current sources when possible |
| Literature-specific claim | "this paper proves", "the authors found", numerical result, DOI, arXiv ID | verify from the paper or a reliable bibliographic source |
| Inference or analogy | teaching analogy, likely motivation, intuitive explanation not directly in source | label as inference or analogy |

## When To Verify

Verify before stating facts about:

- current or latest missions, telescopes, surveys, data releases, APIs, packages, models, leaderboards, or institutional roles;
- specific papers, arXiv IDs, DOI, author claims, figure numbers, table values, and numerical results;
- safety-critical, legal, medical, or financial facts if they appear in a cross-domain question.

Prefer primary sources when available: official mission pages, documentation, paper PDFs, arXiv pages, journal pages, repository documentation, or dataset pages.

## Current-Fact Output Requirement

For any "latest", "recent", "current", "today", release, mission, survey, software-version, or API-status question:

1. state the exact date used for the answer;
2. cite or name the source checked, preferably with a link when the interface supports links;
3. separate the live-status answer from the conceptual explanation;
4. say what remains unverified if no source can be checked.

Silent verification is not enough. The reader must be able to see what was checked.

## Evidence Status Wording

End substantial answers with a short evidence status note. Use one of these patterns:

- "证据状态：这是稳定教材层面的解释，没有使用当前网页信息。"
- "证据状态：概念解释基于稳定背景；关于该论文的说法只基于你给出的段落。"
- "证据状态：当前事实已按官方文档/论文页面核查。"
- "证据状态：下面的类比是教学推断，不等同于论文原文结论。"

For multi-question answers, attach a compact evidence status to each numbered answer or use a final table that maps each question number to its evidence status. Do not provide only one generic evidence note for the whole response when claim types differ.

## Citation Discipline

Do not fabricate:

- DOI, arXiv ID, ADS bibcode, page number, figure number, table number;
- software version, release date, data-release name;
- mission status, instrument parameter, survey area, sample size;
- numerical result or error bar.

If a source is not available, say what can still be explained from general knowledge and what remains unverified.

## Paper Interpretation Boundary

When explaining a paper:

- "作者声称" means the paper states or argues it.
- "这通常意味着" means an interpretation based on field knowledge.
- "这已经被证明" requires verification and should not be used casually.
- A method being plausible is not the same as the result being established.

Use careful language when moving from text to interpretation:

| Safer phrase | Avoid |
| --- | --- |
| "这段话的意思是..." | "事实就是..." |
| "作者在这里假设..." | "宇宙一定..." |
| "这个类比可以帮助理解..." | "这完全等价于..." |
| "如果采用这个模型..." | "红移直接给出距离..." |
