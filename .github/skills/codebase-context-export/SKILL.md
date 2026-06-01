---
name: codebase-context-export
description: 'Export a repository into CODEBASE_CONTEXT.md for large-context models. Use simple mode for broad exports and smart mode for token-budgeted, task-aware context.'
ecosystem: codebase-context
argument-hint: 'Describe the repository, simple or smart mode, any include or exclude rules, an optional budget/task, supporting-file policy, and output path.'
---

# Codebase Context Export

## When To Use
- Build a single markdown file for a model that cannot inspect the repository
  directly.
- Capture the full filtered source tree plus useful supporting files in one
  portable artifact with simple mode.
- Capture a compact task-focused artifact with smart mode, using a low, medium,
  or high token budget and optional task text.
- Honor user-directed pickup rules such as source-only, selected paths, or
  targeted exclusions while preserving the required export template.

## Role
You are the export skill for the codebase-context ecosystem.
Your job is to turn repository content into one markdown file that follows the
required prompt placement while keeping source coverage broad by default and
supporting token-budgeted smart exports when requested.

## Required Inputs
- The target repository root.
- Any explicit include or exclude pickup rules from the user.
- Whether supporting files should use the default automatic policy, all text
  files, or source-only mode.
- Export mode: `simple` for the traditional broad export, or `smart` for a
  token-budgeted export.
- For smart mode, an optional budget preset (`low`, `medium`, or `high`) and
  optional task description.
- An optional output path when the caller does not want the default
  `CODEBASE_CONTEXT.md` destination.

## Procedure
1. Inspect the user request and extract any explicit pickup constraints first.
2. If the user did not ask for a compact export and did not provide `--budget`
   or `--task`, use simple mode.
3. If the user supplies `--budget`, `--task`, or asks for compact task-focused
   context, use smart mode. `--budget` and `--task` imply smart mode when
   `--mode` is omitted.
4. If the user did not narrow the scope, export the full filtered source code
   and add useful supporting files automatically in simple mode.
5. If the user did narrow the scope, translate that request into the shipped
   generator options such as repeated `--include`, repeated `--exclude`, or
   `--source-only`.
6. Exclude ignored, build, cache, and noise directories unless the user
   explicitly asks for a different export scope.
7. Preserve the required markdown template headings exactly:
   `【指示】`, `【インデックス】`, `【コードベース】`, and
   `【念押しの指示】`.
8. In installed target repositories, generate the export with the shipped
   runtime launcher
   [generate_codebase_context.sh](../../ecosystems/codebase-context/generate_codebase_context.sh)
   so the shared installed runtime contract can build and run the disposable
   runtime container. Treat
   [generate_codebase_context.py](../../ecosystems/codebase-context/generate_codebase_context.py).
   as the container-internal implementation.
9. Confirm that the resulting markdown contains a compact directory index and
   that the selected repository files were embedded in deterministic path order.

## Rules
1. Simple mode full filtered source coverage is the default and recommended
   mode.
2. Explicit user pickup rules override the default automatic selection policy.
3. Do not include ignored, build, or cache directories unless the user clearly
   requested them.
4. Do not rewrite the required prompt template into a different structure.
5. Keep installable links inside this skill limited to manifest-owned payload.
6. Treat Docker as the only required host prerequisite for installed-target
   execution of this ecosystem.
7. Do not combine `--mode simple` with `--budget` or `--task`; use smart mode
   for those options.

## Outputs
- A generated markdown export, usually `CODEBASE_CONTEXT.md`
- A short summary of the applied pickup rules
- Validation notes about template order and included scope
