# Documentation Update Rules / 文書更新ルール

## Purpose / 目的

This file is the canonical policy source for documentation updates in this
repository. Read it before creating, rewriting, splitting, merging, or deleting
stable files under `docs/`.

Related canonical docs:
[docs/README.md](./README.md)
[docs/AI_AGENT_INSTRUCTIONS.md](./AI_AGENT_INSTRUCTIONS.md)
[docs/en/ecosystems.md](./en/ecosystems.md)
[docs/ja/ecosystems.ja.md](./ja/ecosystems.ja.md)
[docs/en/project-charter.md](./en/project-charter.md)
[docs/ja/project-charter.ja.md](./ja/project-charter.ja.md)
[docs/en/ubiquitous-language.md](./en/ubiquitous-language.md)
[docs/ja/ubiquitous-language.ja.md](./ja/ubiquitous-language.ja.md)
[docs/TODO.md](./TODO.md)

The project charter is not a generic rules catalog. By default it stays
minimal and records only repository-specific scope and explicit maintainer
decisions. Shared vocabulary belongs in the ubiquitous-language docs.

この文書は、本リポジトリにおける docs 更新ルールの正本です。安定運用する
docs を新規作成、改稿、統合、分割、削除する前に確認します。

プロジェクト憲章は generic なルール集ではありません。既定では最小限に保ち、
repository 固有の目的や前提、maintainer が明示した判断だけを記録します。
共有語彙はユビキタス言語文書で管理します。

## Canonical Document Set / 正本文書セット

| Path | Role | Notes |
|---|---|---|
| docs/README.md | Documentation map | Entry point for readers and agents. |
| docs/AI_AGENT_INSTRUCTIONS.md | Shared AI agent instructions | Tool-neutral operating guidance linked from tool-specific entry points. |
| docs/en/ecosystems.md | English ecosystem inventory reference | Repository-facing summary aligned with the English docs subtree. |
| docs/ja/ecosystems.ja.md | 日本語 ecosystem inventory reference | `docs/en/ecosystems.md` の対応文書。 |
| docs/TODO.md | Operational backlog | Routine maintenance is allowed; structural reorganization requires explicit in-session human instruction. |
| docs/DOCUMENTATION_UPDATE_RULES.md | Documentation governance | Canonical policy source for docs updates. |
| docs/en/project-charter.md | English charter | Repository-specific context and explicit maintainer decisions. It may intentionally remain minimal. |
| docs/ja/project-charter.ja.md | 日本語版憲章 | repository 固有の前提と明示判断。意図的に最小限のままでもよい。 |
| docs/en/ubiquitous-language.md | English ubiquitous language | Shared project vocabulary that agents may maintain for context alignment without adding policy. |
| docs/ja/ubiquitous-language.ja.md | 日本語ユビキタス言語 | 文脈合わせのための共有語彙。方針追加の場にしない。 |

The `.ai_ecosystems/` tree remains the canonical implementation-facing source
for manifests, agents, skills, runtime payload, routing, and delivery behavior. Stable docs should
describe those artifacts clearly without duplicating their entire content.

When the repository already has a clear stable docs grouping such as `docs/en`
and `docs/ja`, place new repository-facing docs inside that structure and
reuse neighboring naming conventions. Only create a new root-level document
under `docs/` when no clearer placement guidance exists.

`.ai_ecosystems/` 配下の ecosystem files は、manifest、agents、skills、
runtime payload、routing、installer 挙動の実装向け正本です。stable docs は、
それらの内容を丸ごと複製せずに明快に説明します。

`docs/en` と `docs/ja` のような明確な stable docs 構造がすでにある場合は、
新しい repository-facing docs もその構造に合わせ、近傍の命名規則を再利用します。
より明確な配置指針がない場合に限って、`docs/` 直下の新規文書を許可します。

## Update Triggers / 更新トリガー

- Project-specific scope or explicit maintainer decisions changed and a
  maintainer explicitly instructed charter edits: update the charter in the
  same change. /
  repository 固有の目的や前提、maintainer が明示した判断が変わり、かつ
  maintainer が憲章編集を明示的に指示した場合は、同じ変更で憲章を更新する。
- Shared project vocabulary or context-alignment terminology changed:
  update the ubiquitous-language docs in the same change. Update the charter
  only if a maintainer explicitly instructs editing it. /
  共有語彙や文脈合わせの用語が変わった場合は、同じ変更でユビキタス言語文書を
  更新する。憲章は maintainer が明示的に編集指示したときだけ更新する。
- Ecosystem registry, manifest, delivery helper, or validator behavior
  changed: update the docs that explain that behavior in the same change, and
  update the charter only when project-specific decisions also changed. /
  ecosystem registry、manifest、delivery helper、validator の挙動が変わった
  場合は、その挙動を説明する文書を同じ変更で更新し、project 固有判断にも変更
  があるときだけ憲章を更新する。
- Current ecosystem inventory or manifest-scoped membership changed: update
  the language-specific ecosystem inventory docs in the same change, such as
  `docs/en/ecosystems.md` and `docs/ja/ecosystems.ja.md`. /
  現在の ecosystem inventory または manifest に紐づく membership が変わった
  場合は、同じ変更で `docs/en/ecosystems.md` と
  `docs/ja/ecosystems.ja.md` のような対応文書を更新する。
- Documentation structure changed: update `docs/README.md`, `README.md`,
  `AGENTS.md`, `CLAUDE.md`, and any `docs/TODO.md` references in the same
  change. /
  文書構成が変わった場合は、`docs/README.md`、`README.md`、`AGENTS.md`、
  `CLAUDE.md`、および `docs/TODO.md` からの参照を同じ変更で更新する。
- Keep paired English and Japanese documents structurally aligned in the same
  change. /
  英語版と日本語版の対応文書は、同じ変更で構造を揃える。
- Before any docs-only rewrite, read the charter when repository-specific
  context matters and read the ubiquitous-language docs when terminology or
  context alignment matters. If the charter is minimal, rely on this file,
  the ubiquitous-language docs, and the implementation-facing docs first. /
  docs の改稿に入る前は、repository 固有の前提が関係する場合に憲章を確認し、
  用語や文脈合わせが関係する場合にユビキタス言語文書を確認する。憲章が最小限
  なら、この文書、ユビキタス言語文書、実装側文書を先に参照する。

## Placement And Rewrite Rules / 配置と再構成ルール

- Keep the split explicit between repository-level overview docs and
  implementation-facing `.ai_ecosystems` artifacts. /
  repository-level の概要文書と、実装向け `.ai_ecosystems` artifacts の分離を
  明示したまま保つ。
- In bilingual repositories, reserve root `docs/` files for shared navigation
  and governance artifacts, and place topical reference docs as paired
  language files under the existing language directories. /
  英日対応 repository では、root の `docs/` を共有の案内文書とガバナンス文書に
  限定し、topic ごとの参照文書は既存の言語別ディレクトリ配下の対応文書として
  配置する。
- Reuse neighboring file naming conventions for new docs. When the repository
  already uses lowercase kebab-case files in language-specific directories,
  continue that pattern. /
  新規 docs は近傍の命名規則を再利用する。言語別ディレクトリで lowercase
  kebab-case を使っている場合は、そのパターンを継続する。
- Keep ubiquitous-language docs descriptive. They may help align terminology,
  but they must not become a backdoor policy surface. /
  ユビキタス言語文書は記述的に保つ。用語合わせには使えるが、方針を増殖させる
  抜け道にしてはならない。
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
Keep the set of diagram families intentionally small and prefer tables for
ecosystem inventories or routing summaries.

Mermaid は、本文や表より理解効率が明確に上がる場合に限って使います。ecosystem
inventory や routing summary は、まず表を優先します。

## Validation Checklist / 検証チェックリスト

1. `docs/README.md` still routes readers to the canonical docs.
2. `README.md`, `AGENTS.md`, and `CLAUDE.md` still link to `docs/README.md`
   and this file.
3. English and Japanese charter counterparts remain aligned.
4. English and Japanese ubiquitous-language counterparts remain aligned.
5. `docs/TODO.md` edits are either routine maintenance or explicitly approved
   structural reorganization.
6. Relative links remain valid after file moves or renames.
7. Additional bilingual reference docs follow the established language-specific
  directory structure unless the repository has no clearer placement guide.
8. `.ai_ecosystems/README.md` and installed ecosystem manifests still
  match the current installed ecosystems.

## Skill Compatibility Contract / Skill 互換契約

- Trigger phrases: `rewrite docs`, `sync docs with code`, `update docs map`,
  `ecosystem documentation`, `documentation governance`. /
  trigger phrase は docs 同期や ecosystem documentation 更新を示す語を含める。
- Required inputs: changed files, affected ecosystem behavior, current docs map,
  and language mode. /
  必須入力は差分対象、影響する ecosystem behavior、docs map、言語モード。
- Expected outputs: updated docs, updated navigation links, deleted superseded
  sections when needed, and a short validation summary. /
  期待出力は更新済み文書、更新済み導線、必要時の旧節削除、短い検証要約。
- Forbidden shortcuts: leaving stale sections in place, updating one language
  only, and autonomously restructuring `docs/TODO.md` without explicit
  in-session human instruction. /
  禁止事項は、残骸節の放置、片言語のみの更新、明示的な人手指示なしの
  `docs/TODO.md` 構成再編。
