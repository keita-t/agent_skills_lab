# 現在の ecosystem 一覧

この文書は、このリポジトリで現在管理している ecosystem を要約した一覧です。
実装向け inventory は
[.ai_ecosystems/README.md](../../.ai_ecosystems/README.md) に集約し、
各 ecosystem の定義は `.ai_ecosystems/` 配下の manifest に紐づきます。
`.ai_ecosystems/` 直下の共有ファイルは共有インフラであり、
それ自体は別 ecosystem ではありません。

## 関連文書

- [docs/README.md](../README.md): ドキュメント案内と読書順。
- [docs/en/ecosystems.md](../en/ecosystems.md): 英語版の対応文書。

## スナップショット

- Active ecosystem 数: 3
- 現在の ecosystem slug: `ecosystem-audit`、`codebase-context`、`repository-docs`
- 現在の主責務: 共有 ecosystem 監査と仕事の質フィードバック、large-context model 向けの repository codebase export、repository documentation governance、docs refactoring、bootstrap、TODO progress tracking。
- manifest の方向性: ownership と dependency の structural contract を優先する。

## Installed Runtime Contract

- installed runtime は ecosystem 共通の optional contract。
- runtime-free ecosystem は runtime metadata を持たず、install 後 runtime を同梱しない。
- runtime-enabled ecosystem は manifest frontmatter に `runtime-mode`、
	`runtime-entrypoint`、`runtime-requires` を宣言できる。
- ecosystem は `shared-ownership-files` も宣言でき、複数の install 済み
	ecosystem が明示的に co-own してよい manifest-owned path を指定する。
- runtime asset 自体は引き続き `ecosystem-files` に属し、runtime metadata は
	target host 上での実行方法だけを記述する。
- delivery は、すべての owner ecosystem が同じ path を
	`shared-ownership-files` で明示した場合にだけ、その manifest-owned path を
	重複 install できるものとして扱う。remove では最後の installed owner が
	消えるまでその path を保持する。
- 現在サポートする installed runtime mode は `container` のみで、manifest-owned
	launcher と disposable Docker execution を共通契約とする。
- runtime-enabled launcher は、host Docker daemon から現在の workspace path が
	直接見えない場合に備えて、bind-mount probe と `docker cp` fallback transport
	を共有 helper `.ai_ecosystems/runtime_container_lib.sh` で再利用できる。

## AI Tool Host Delivery

- manifest の `agents` と `skills` は logical member name として扱い、正本
	file は `.ai_ecosystems/<slug>/agents/` と
	`.ai_ecosystems/<slug>/skills/` に置く。
- delivery host adapter が、その正本 file を選択された AI tool の native path
	へ copy する。GitHub Copilot は `.github/agents/` と `.github/skills/`、
	Claude Code は `.claude/agents/` と `.claude/skills/`、Codex は
	`.agents/skills/`、Cursor は `.cursor/skills/` を使う。
- host が指定されない場合、delivery は target repository の marker を検出し、
	検出されたすべての host に install する。marker がない場合は
	互換性のため GitHub Copilot に fallback する。
- delivery は target repository の `AGENTS.md`、`CLAUDE.md`、
	`.github/copilot-instructions.md` のような root/global instructions を変更しない。

## 現在の Inventory

| Slug | Status | Purpose | Root agent | Skills | Notes |
|---|---|---|---|---|---|
| `ecosystem-audit` | `active` | ecosystem manifest、install 済み payload、仕事の質を rubric-first で監査する共通 platform。 | `ecosystem-audit.agent.md` | なし | 他 repository へ install でき、manifest の `audit-files` で各 ecosystem から拡張できる。 |
| `codebase-context` | `active` | repository を large-context model 向けの単一 markdown context file に export する。 | `codebase-context.agent.md` | `codebase-context-export` | 他 repository へ install できる。`simple` mode は既定で full filtered source code と useful supporting files を export し、`smart` mode は token-budgeted かつ task-aware な選定を行う。ユーザーの明示 pickup rule がある場合はその指定で scope を上書きする。shared installed runtime contract に `container` mode で opt-in している。 |
| `repository-docs` | `active` | repository documentation governance、docs refactoring、bootstrap、TODO progress tracking。 | `governance-repository-context-manager.agent.md` | `docs-bootstrap`、`docs-sync`、`docs-refactor`、`todo-maintenance` | この repository 自身で self-host しつつ、他 repository へ install できる。`ecosystem-audit` に依存し、docs 専用の audit pack を同梱し、installed runtime は宣言しない。 |

## Ecosystem Details

### `ecosystem-audit`

正本 manifest:
[.ai_ecosystems/ecosystem-audit/ECOSYSTEM.md](../../.ai_ecosystems/ecosystem-audit/ECOSYSTEM.md)

| 項目 | 現在の実装 |
|---|---|
| Root agent | [.ai_ecosystems/ecosystem-audit/agents/ecosystem-audit.agent.md](../../.ai_ecosystems/ecosystem-audit/agents/ecosystem-audit.agent.md) |
| Skills | なし |
| Ownership contract | agent、listed ecosystem-owned files、listed audit files、および manifest 自体 |
| Ecosystem 固有 files | `.ai_ecosystems/ecosystem-audit/assets/` 配下の starter asset |
| Audit files | `.ai_ecosystems/ecosystem-audit/audit/` 配下の shared core rules、report contract、work-quality rubric |
| 拡張モデル | 他 ecosystem は manifest の `audit-files` で追加の audit file を宣言し、ecosystem 固有の監査責務を自分で所有する |
| Starter asset | 新しい ecosystem 向けの audit pack template と manual smoke scenario を同梱する |
| 出力モデル | 品質次元ごとの要約を先に出し、その後に根拠付き所見を続ける rubric-first report |

#### 監査レポート例

次の短い例は、rubric-first 監査レポートの既定形を示します。

```md
1. Scope summary
	- `repository-docs` を install した target repository に対する監査
	- shared core rules、shared work-quality rubric、repository-docs audit pack を適用

2. Rubric summary
	| Dimension | Rating | Evidence basis | Confidence | Short rationale |
	|---|---|---|---|---|
	| clarity | Acceptable | artifact-observed | high | install 済み docs は canonical entrypoint へ到達できるが、bootstrap の導線はまだ複数ファイルの往復が必要。 |
	| constraint-adherence | Strong | artifact-observed | high | install 済み guidance は manifest-owned payload の内側に収まり、source-only helper を参照しない。 |
	| recovery-behavior | Needs Work | definition-inferred | medium | 定常系の流れは説明できているが、runtime example がないため missing context からの回復導線はまだ薄い。 |

3. Findings
	- warning
	  - Dimension: recovery-behavior
	  - Rule source: `.ai_ecosystems/repository-docs/audit/repository-docs-audit.md`
	  - Evidence basis: definition-inferred
	  - Confidence: medium
	  - Impact: install 済み docs が一部欠けたとき、maintainer は正常系は理解できても回復手順に迷いやすい。
	  - Path: `docs/README.md`
	  - Message: recovery guidance は開始点は示すが、canonical doc が 1 つ欠けた場合の戻し方までは示していない。
	  - Improvement feedback: upstream-ecosystem-feedback - install 済み guidance に missing-doc recovery の短い分岐を 1 つ追加する。

4. Files and manifests inspected
	- `.ai_ecosystems/repository-docs/ECOSYSTEM.md`
	- `docs/README.md`
	- `.ai_ecosystems/repository-docs/agents/governance-repository-context-manager.agent.md`

5. Suggested follow-up
	- install 済み docs セットが不完全な場合の recovery step を 1 つ追加する。
	- upstream guidance 反映後に再監査する。
```

### `codebase-context`

正本 manifest:
[.ai_ecosystems/codebase-context/ECOSYSTEM.md](../../.ai_ecosystems/codebase-context/ECOSYSTEM.md)

| 項目 | 現在の実装 |
|---|---|
| Root agent | [.ai_ecosystems/codebase-context/agents/codebase-context.agent.md](../../.ai_ecosystems/codebase-context/agents/codebase-context.agent.md) |
| Skills | [.ai_ecosystems/codebase-context/skills/codebase-context-export/SKILL.md](../../.ai_ecosystems/codebase-context/skills/codebase-context-export/SKILL.md) |
| Ownership contract | agent、skill、listed ecosystem-owned files、listed audit files、および manifest 自体 |
| Dependencies | `ecosystem-audit` |
| Ecosystem 固有 files | 共有 helper `.ai_ecosystems/runtime_container_lib.sh` と、`.ai_ecosystems/codebase-context/` 配下の runtime Dockerfile、shell launcher、generator |
| Audit files | `.ai_ecosystems/codebase-context/audit/codebase-context-audit.md` |
| Installed runtime | shared installed runtime contract の `container` mode。`generate_codebase_context.sh` を runtime launcher、`.ai_ecosystems/runtime_container_lib.sh` を共有 transport helper とし、host prerequisite は Docker のみ |
| 品質観点 | export の有用性、signal-to-noise、pickup rule の順守、operator experience |
| 既定の export 挙動 | `simple` mode で repository root の `CODEBASE_CONTEXT.md` を生成し、full filtered source code と useful supporting files を 1 つの markdown snapshot にまとめる |
| Smart export 挙動 | `smart` mode は `--budget low|medium|high` と任意の `--task` text を使い、full/stub representation を組み合わせた token-budgeted かつ task-aware な snapshot を生成する |
| ユーザー override rule | include、exclude、source-only などの明示 pickup rule がある場合は、既定の broad export policy よりその指定を優先する |
| Runtime output | 生成された markdown snapshot は runtime output であり、manifest-owned install payload には含めない |
| Installed-target smoke | [tests/sandbox/run_codebase_context_container_smoke.sh](../../tests/sandbox/run_codebase_context_container_smoke.sh) が、共有の [tests/sandbox/base/Dockerfile](../../tests/sandbox/base/Dockerfile) を使って一時 target repository を準備し、その後 install 済み runtime launcher を直接呼び出す。export 自体の実行境界は runtime container の 1 回だけになる。 |

### `repository-docs`

正本 manifest:
[.ai_ecosystems/repository-docs/ECOSYSTEM.md](../../.ai_ecosystems/repository-docs/ECOSYSTEM.md)

| 項目 | 現在の実装 |
|---|---|
| Root agent | [.ai_ecosystems/repository-docs/agents/governance-repository-context-manager.agent.md](../../.ai_ecosystems/repository-docs/agents/governance-repository-context-manager.agent.md) |
| Specialized agents | [.ai_ecosystems/repository-docs/agents/governance-ecosystem-manifest.agent.md](../../.ai_ecosystems/repository-docs/agents/governance-ecosystem-manifest.agent.md), [.ai_ecosystems/repository-docs/agents/governance-ecosystem-delivery.agent.md](../../.ai_ecosystems/repository-docs/agents/governance-ecosystem-delivery.agent.md) |
| Skills | [.ai_ecosystems/repository-docs/skills/docs-bootstrap/SKILL.md](../../.ai_ecosystems/repository-docs/skills/docs-bootstrap/SKILL.md), [.ai_ecosystems/repository-docs/skills/docs-sync/SKILL.md](../../.ai_ecosystems/repository-docs/skills/docs-sync/SKILL.md), [.ai_ecosystems/repository-docs/skills/docs-refactor/SKILL.md](../../.ai_ecosystems/repository-docs/skills/docs-refactor/SKILL.md), [.ai_ecosystems/repository-docs/skills/todo-maintenance/SKILL.md](../../.ai_ecosystems/repository-docs/skills/todo-maintenance/SKILL.md) |
| Ownership contract | agents、skills、listed ecosystem-owned files、listed audit files、および manifest 自体 |
| Dependencies | `ecosystem-audit` |
| Ecosystem 固有 files | `.ai_ecosystems/repository-docs/` 配下の template assets |
| Audit files | `.ai_ecosystems/repository-docs/audit/repository-docs-audit.md` |
| Installed runtime | 宣言なし。install 後に実行する executable runtime は持たない。 |
| Install portability rule | installable markdown 内の repository-local link は manifest-owned payload の内側で解決できなければならず、install 後の artifact は target repository 内で self-contained に保つ。 |
| 品質観点 | 文書の clarity、コードベースとの整合、自然言語としての読みやすさ、図解の適切さ、英日整合の質、operator usability |
| Audit flow | shared `ecosystem-audit` platform が shared core rules、shared work-quality rubric、この ecosystem の audit pack を on-demand で適用する |
| Installed-target smoke | [tests/sandbox/run_repository_docs_container_smoke.sh](../../tests/sandbox/run_repository_docs_container_smoke.sh) が、一時 repository へ ecosystem を install し、shipped bilingual template pack を適用したうえで、共有の [tests/sandbox/base/Dockerfile](../../tests/sandbox/base/Dockerfile) から build した repo 同梱 Docker sandbox 内で smoke test を実行する。 |

## Validation

この repository は現在 GitHub Actions workflow を install していません。
検証が必要な場合は local で `python -m pytest -q` を実行します。
`tests/sandbox/` 配下の sandbox smoke script は、install 済み target の
手動確認用として残します。

## 共有 Ecosystem Infrastructure

次のファイルは、ecosystem 全体を支える共有基盤であり、個別 ecosystem entry
ではありません。

| Path | 役割 |
|---|---|
| [.ai_ecosystems/deliver_ecosystem.py](../../.ai_ecosystems/deliver_ecosystem.py) | 宣言された dependency も含めて manifest-owned install/remove workflow を target `owner/repo` に適用し、PR ベース delivery を準備する。 |
| [.ai_ecosystems/runtime_container_lib.sh](../../.ai_ecosystems/runtime_container_lib.sh) | install 済み `container` runtime 向けの共有 shell transport helper。bind-mount probe と、Docker host が現在の workspace path を解決できない場合の `docker cp` fallback 実行を担う。 |
