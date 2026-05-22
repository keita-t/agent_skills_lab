# Documentation Update Rules / 文書更新ルール

## Purpose / 目的

This file is the canonical policy source for documentation updates in this
repository. Read it before creating, rewriting, splitting, merging, or deleting
stable files under `docs/`.

Related canonical docs:
[docs/README.md](./README.md)
[docs/en/project-charter.md](./en/project-charter.md)
[docs/ja/project-charter.ja.md](./ja/project-charter.ja.md)
[docs/TODO.md](./TODO.md)

The project charter is not a generic rules catalog. By default it stays
minimal and records only repository-specific scope, terminology, and explicit
maintainer decisions.

この文書は、本リポジトリにおける docs 更新ルールの正本です。安定運用する
docs を新規作成、改稿、統合、分割、削除する前に確認します。

プロジェクト憲章は generic なルール集ではありません。既定では最小限に保ち、
repository 固有の目的、用語、maintainer が明示した判断だけを記録します。

## Canonical Document Set / 正本文書セット

| Path | Role | Notes |
|---|---|---|
| docs/README.md | Documentation map | Entry point for readers and agents. |
| docs/TODO.md | Operational backlog | Routine maintenance is allowed; structural reorganization requires explicit in-session human instruction. |
| docs/DOCUMENTATION_UPDATE_RULES.md | Documentation governance | Canonical policy source for docs updates. |
| docs/en/project-charter.md | English charter | Repository-specific context and explicit maintainer decisions. It may intentionally remain minimal. |
| docs/ja/project-charter.ja.md | 日本語版憲章 | repository 固有の前提と明示判断。意図的に最小限のままでもよい。 |

If the repository needs additional permanent docs, extend `docs/README.md` in
the same change and keep paired-language responsibilities explicit.

追加の恒久文書が必要な場合は、同じ変更で `docs/README.md` を更新し、対応
言語ごとの責務を明示します。

## Update Triggers / 更新トリガー

- Project-specific scope, terminology, or explicit maintainer decisions
  changed: update the charter in the same change. /
  repository 固有の目的、用語、maintainer が明示した判断が変わった場合は、
  同じ変更で憲章を更新する。
- Public contract changed: update the affected reference or overview docs in
  the same change. /
  公開契約が変わった場合は、関連する概要文書または参照文書を同じ変更で更新する。
- Implementation behavior or developer workflow changed: update the docs that
  explain that behavior in the same change. /
  実装挙動または開発ワークフローが変わった場合は、その挙動を説明する文書を
  同じ変更で更新する。
- Documentation structure changed: update `docs/README.md`, `README.md`,
  `CLAUDE.md`, and any `docs/TODO.md` references in the same change. /
  文書構成が変わった場合は、`docs/README.md`、`README.md`、`CLAUDE.md`、
  および `docs/TODO.md` からの参照を同じ変更で更新する。
- Keep paired English and Japanese documents structurally aligned in the same
  change. /
  英語版と日本語版の対応文書は、同じ変更で構造を揃える。
- Before any docs-only rewrite, read the charter when repository-specific
  context matters. If the charter is minimal, rely on this file and the
  implementation-facing docs first. /
  docs の改稿に入る前は、repository 固有の前提が関係する場合に憲章を確認する。
  憲章が最小限なら、この文書と実装側文書を先に参照する。

## Placement And Rewrite Rules / 配置と再構成ルール

- Keep the split explicit between overview-style docs and implementation-style
  docs. /
  概要文書と実装文書の役割分担を明示したまま保つ。
- Use crosswalk-first planning before large rewrites. /
  大きな改稿の前に、既存節の移し先を先に決める。
- Do not leave stale summary sections behind after content has moved. /
  内容を移した後に古い要約節を残さない。
- Keep claims anchored to implemented behavior, not future intent. /
  記述は将来意図ではなく現行実装に紐付ける。
- `docs/TODO.md` may receive routine maintenance as normal work. Structural
  reorganization is allowed only on an explicit in-session human instruction. /
  `docs/TODO.md` の通常保守は許可するが、構成再編はセッション内での明示指示
  がある場合に限る。

## Quality Bar / 品質基準

Every moved or rewritten section should fit one clear granularity level.

移設または改稿した節は、明確な 1 つの粒度ラベルに当てはめます。

| Label | Expected scale | Use |
|---|---|---|
| Snapshot | 3-5 sentences | Quick orientation and caveats. |
| Overview | 1-2 paragraphs | Responsibilities and current design intent. |
| Table | 1 main table | Stable inventories and maps. |
| Flow | 5-8 ordered steps | Ordered behavior and lifecycle flows. |
| Checklist | 5-8 items | Update rules, extension steps, validation gates. |
| Reference | Complete structured coverage | Detailed stable contracts. |

## Mermaid Policy / Mermaid 利用方針

Use Mermaid only when it materially improves comprehension over text or tables.
Keep the set of diagram families intentionally small.

Mermaid は、本文や表より理解効率が明確に上がる場合に限って使います。図の
種類は少数に抑えます。

## Validation Checklist / 検証チェックリスト

1. `docs/README.md` still routes readers to the canonical docs.
2. `README.md` and `CLAUDE.md` still link to `docs/README.md` and this file.
3. English and Japanese charter counterparts remain aligned.
4. `docs/TODO.md` edits are either routine maintenance or explicitly approved
   structural reorganization.
5. Relative links remain valid after file moves or renames.

## Skill Compatibility Contract / Skill 互換契約

- Trigger phrases: `rewrite docs`, `sync docs with code`, `update docs map`,
  `bilingual docs`, `documentation governance`. /
  trigger phrase は docs 同期や英日対応更新を示す語を含める。
- Required inputs: changed files, affected contracts or workflows, current docs
  map, and language mode. /
  必須入力は差分対象、影響する契約やワークフロー、docs map、言語モード。
- Expected outputs: updated docs, updated navigation links, deleted superseded
  sections when needed, and a short validation summary. /
  期待出力は更新済み文書、更新済み導線、必要時の旧節削除、短い検証要約。
- Forbidden shortcuts: leaving stale sections in place, updating one language
  only, and autonomously restructuring `docs/TODO.md` without explicit
  in-session human instruction. /
  禁止事項は、残骸節の放置、片言語のみの更新、明示的な人手指示なしの
  `docs/TODO.md` 構成再編。