---
name: word
description: Create, edit, convert, polish, and verify Microsoft Word `.docx` documents. Use when the user mentions Word, DOCX, `.docx`, 写成 Word, 转成 Word, Word 初稿, Word 排版, 修改 Word 文档, 渲染检查 Word, or asks for a document deliverable that should open cleanly in Microsoft Word.
---

# Word

## Overview

Use this skill as the lightweight Word-specific router. For substantial `.docx` work, load and follow the existing `documents` skill first; it contains the detailed DOCX creation, editing, OOXML, and render-QA workflow.

## Core Workflow

1. Treat `.docx` as the final deliverable unless the user asks for another format.
2. If the `documents` skill is available, read its `SKILL.md` and follow its workflow, especially the render-to-PNG visual QA gate.
3. Use bundled workspace dependencies for document work; avoid relying on random system Python/Node packages when the bundled runtime is available.
4. For new documents, choose an appropriate document preset from the `documents` skill. For academic drafts and research reports, prefer a clean formal report style with readable headings, tables, and formula blocks.
5. Preserve mathematical notation. For scientific Word documents, convert LaTeX math to Word-native Office Math OMML; do not leave raw `\(...\)`, `\[...\]`, `\frac`, `\log`, or similar LaTeX source in normal document text unless the user explicitly asks for source notation.
6. For tables, use real Word tables with explicit widths, padding, and repeat headers when appropriate. Do not fake tables with plain text.
7. For headings and lists, use real Word styles and numbering/list structures rather than manual formatting.
8. Render and inspect the DOCX before delivery when `soffice`/LibreOffice or another reliable renderer is available.
9. If visual rendering is unavailable, still create the DOCX, run structural checks where possible, and explicitly tell the user that visual render QA was skipped.
10. Final responses should link to the final `.docx` and mention only important QA limitations.

## Common Requests

- "写成 Word" or "转成 Word": convert the current Markdown/text draft into a `.docx`, preserving hierarchy, tables, code blocks, and formulas.
- "Word 排版": improve styles, spacing, headings, tables, and page breaks while preserving content.
- "修改这个 Word": make local edits to the existing document; preserve original structure unless the user asks for a rewrite.
- "生成论文初稿 Word": create a formal research draft `.docx` with title, abstract, sections, equations, tables, and figure placeholders.

## Quality Rules

- Prefer a clean, readable document over decorative styling.
- Keep formulas, code paths, commands, and configuration keys accurate.
- For LaTeX math, prefer the pipeline LaTeX -> MathML -> OMML using `latex2mathml` and Microsoft Office `MML2OMML.XSL` when available. After generation, inspect `word/document.xml` and require `<m:oMath>` objects plus no leftover raw LaTeX delimiters in ordinary text.
- Do not silently drop images, tables, equations, citations, or figure placeholders.
- Do not claim the document passed visual QA unless rendered pages were actually inspected.
