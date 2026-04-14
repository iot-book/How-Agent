---
name: markdown_reader
description: Use this skill to read a Markdown source file first, then extract and explain its key points in a beginner-friendly way.
---
# Markdown Reader Skill

## Purpose
This skill is used for tasks where the agent should first read a Markdown document, then organize the document into a clearer explanation, summary, or study note.

## When To Use
- The task asks to explain, summarize, or整理 a Markdown file
- The answer should come from an actual source file, not from guessing
- The output should help beginners quickly understand the source material

## Workflow
1. Identify the source Markdown file that should be read
2. Read the file before giving any conclusion
3. Extract the document title, key sections, and core points
4. Reorganize the result into a concise beginner-facing explanation
5. If the file cannot be read, clearly explain what is missing

## Tool Use Rules
- Prefer using a file-reading tool before answering
- Do not invent content that is not present in the source file
- If the source file is missing, report that directly

## Output Style
- Use clear Markdown headings
- Prefer short paragraphs and short bullet lists
- Explain the document in plain language
- Keep the structure stable and easy to scan

## Current Task
$ARGUMENTS
