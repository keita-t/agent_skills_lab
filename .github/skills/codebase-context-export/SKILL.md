---
name: codebase-context-export
description: 'Export a repository into CODEBASE_CONTEXT.md for large-context models. Use when you need one markdown file containing the full codebase, useful supporting files, or a user-directed subset.'
ecosystem: codebase-context
argument-hint: 'Describe the repository, any include or exclude rules, whether supporting files should be auto-selected, and an optional output path.'
---

# Codebase Context Export

## When To Use
- Build a single markdown file for a model that cannot inspect the repository
  directly.
- Capture the full filtered source tree plus useful supporting files in one
  portable artifact.
- Honor user-directed pickup rules such as source-only, selected paths, or
  targeted exclusions while preserving the required export template.

## Role
You are the export skill for the codebase-context ecosystem.
Your job is to turn repository content into one markdown file that follows the
required prompt placement while keeping source coverage broad by default.

## Required Inputs
- The target repository root.
- Any explicit include or exclude pickup rules from the user.
- Whether supporting files should use the default automatic policy, all text
  files, or source-only mode.
- An optional output path when the caller does not want the default
  `CODEBASE_CONTEXT.md` destination.

## Procedure
1. Inspect the user request and extract any explicit pickup constraints first.
2. If the user did not narrow the scope, export the full filtered source code
   and add useful supporting files automatically.
3. If the user did narrow the scope, translate that request into the shipped
   generator options such as repeated `--include`, repeated `--exclude`, or
   `--source-only`.
4. Exclude ignored, build, cache, and noise directories unless the user
   explicitly asks for a different export scope.
5. Preserve the required markdown template headings exactly:
   `【指示】`, `【インデックス】`, `【コードベース】`, and
   `【念押しの指示（最後に小さく）】`.
6. Generate the export with
   [generate_codebase_context.sh](../../ecosystems/codebase-context/generate_codebase_context.sh)
   or
   [generate_codebase_context.py](../../ecosystems/codebase-context/generate_codebase_context.py).
7. Confirm that the resulting markdown contains a compact directory index and
   that the selected repository files were embedded in deterministic path order.

## Rules
1. Full filtered source coverage is the default and recommended mode.
2. Explicit user pickup rules override the default automatic selection policy.
3. Do not include ignored, build, or cache directories unless the user clearly
   requested them.
4. Do not rewrite the required prompt template into a different structure.
5. Keep installable links inside this skill limited to manifest-owned payload.

## Outputs
- A generated markdown export, usually `CODEBASE_CONTEXT.md`
- A short summary of the applied pickup rules
- Validation notes about template order and included scope