# 現在の ecosystem 一覧

この文書は、このリポジトリで現在管理している ecosystem を要約した一覧です。
実装向け inventory は
[.github/ecosystems/README.md](../../.github/ecosystems/README.md) に集約し、
各 ecosystem の定義は `.github/ecosystems/` 配下の manifest に紐づきます。
`.github/ecosystems/` 直下の共有ファイルは共有インフラであり、
それ自体は別 ecosystem ではありません。

## 関連文書

- [docs/README.md](../README.md): ドキュメント案内と読書順。
- [docs/en/ecosystems.md](../en/ecosystems.md): 英語版の対応文書。

## スナップショット

- Active ecosystem 数: 3
- 現在の ecosystem slug: `ecosystem-audit`、`codebase-context`、`repository-governance`
- 現在の主責務: 共有 ecosystem 監査と仕事の質フィードバック、large-context model 向けの repository codebase export、repository documentation governance、bootstrap、TODO progress tracking。
- manifest の方向性: ownership と dependency の structural contract を優先する。

## 現在の Inventory

| Slug | Status | Purpose | Root agent | Skills | Notes |
|---|---|---|---|---|---|
| `ecosystem-audit` | `active` | ecosystem manifest、install 済み payload、仕事の質を rubric-first で監査する共通 platform。 | `ecosystem-audit.agent.md` | なし | 他 repository へ install でき、manifest の `audit-files` で各 ecosystem から拡張できる。 |
| `codebase-context` | `active` | repository を large-context model 向けの単一 markdown context file に export する。 | `codebase-context.agent.md` | `codebase-context-export` | 他 repository へ install できる。既定では full filtered source code と useful supporting files を export し、ユーザーの明示 pickup rule がある場合はその指定で scope を上書きする。 |
| `repository-governance` | `active` | repository documentation governance、bootstrap、TODO progress tracking。 | `governance-repository-context-manager.agent.md` | `repository-governance-bootstrap`、`repository-doc-governance`、`todo-progress-governance` | この repository 自身で self-host しつつ、他 repository へ install できる。`ecosystem-audit` に依存し、governance 専用の audit pack を同梱する。 |

## Ecosystem Details

### `ecosystem-audit`

正本 manifest:
[.github/ecosystems/ecosystem-audit/ECOSYSTEM.md](../../.github/ecosystems/ecosystem-audit/ECOSYSTEM.md)

| 項目 | 現在の実装 |
|---|---|
| Root agent | [.github/agents/ecosystem-audit.agent.md](../../.github/agents/ecosystem-audit.agent.md) |
| Skills | なし |
| Ownership contract | agent、listed ecosystem-owned files、listed audit files、および manifest 自体 |
| Ecosystem 固有 files | `.github/ecosystems/ecosystem-audit/assets/` 配下の starter asset |
| Audit files | `.github/ecosystems/ecosystem-audit/audit/` 配下の shared core rules、report contract、work-quality rubric |
| 拡張モデル | 他 ecosystem は manifest の `audit-files` で追加の audit file を宣言し、ecosystem 固有の監査責務を自分で所有する |
| Starter asset | 新しい ecosystem 向けの audit pack template と manual smoke scenario を同梱する |
| 出力モデル | 品質次元ごとの要約を先に出し、その後に根拠付き所見を続ける rubric-first report |

#### 監査レポート例

次の短い例は、rubric-first 監査レポートの既定形を示します。

```md
1. Scope summary
	- `repository-governance` を install した target repository に対する監査
	- shared core rules、shared work-quality rubric、governance audit pack を適用

2. Rubric summary
	| Dimension | Rating | Evidence basis | Confidence | Short rationale |
	|---|---|---|---|---|
	| clarity | Acceptable | artifact-observed | high | install 済み docs は canonical entrypoint へ到達できるが、bootstrap の導線はまだ複数ファイルの往復が必要。 |
	| constraint-adherence | Strong | artifact-observed | high | install 済み guidance は manifest-owned payload の内側に収まり、source-only helper を参照しない。 |
	| recovery-behavior | Needs Work | definition-inferred | medium | 定常系の流れは説明できているが、runtime example がないため missing context からの回復導線はまだ薄い。 |

3. Findings
	- warning
	  - Dimension: recovery-behavior
	  - Rule source: `.github/ecosystems/repository-governance/audit/repository-governance-audit.md`
	  - Evidence basis: definition-inferred
	  - Confidence: medium
	  - Impact: install 済み docs が一部欠けたとき、maintainer は正常系は理解できても回復手順に迷いやすい。
	  - Path: `docs/README.md`
	  - Message: recovery guidance は開始点は示すが、canonical doc が 1 つ欠けた場合の戻し方までは示していない。
	  - Improvement feedback: upstream-ecosystem-feedback - install 済み guidance に missing-doc recovery の短い分岐を 1 つ追加する。

4. Files and manifests inspected
	- `.github/ecosystems/repository-governance/ECOSYSTEM.md`
	- `docs/README.md`
	- `.github/agents/governance-repository-context-manager.agent.md`

5. Suggested follow-up
	- install 済み docs セットが不完全な場合の recovery step を 1 つ追加する。
	- upstream guidance 反映後に再監査する。
```

### `codebase-context`

正本 manifest:
[.github/ecosystems/codebase-context/ECOSYSTEM.md](../../.github/ecosystems/codebase-context/ECOSYSTEM.md)

| 項目 | 現在の実装 |
|---|---|
| Root agent | [.github/agents/codebase-context.agent.md](../../.github/agents/codebase-context.agent.md) |
| Skills | [.github/skills/codebase-context-export/SKILL.md](../../.github/skills/codebase-context-export/SKILL.md) |
| Ownership contract | agent、skill、listed ecosystem-owned files、listed audit files、および manifest 自体 |
| Dependencies | `ecosystem-audit` |
| Ecosystem 固有 files | `.github/ecosystems/codebase-context/` 配下の generator と shell wrapper |
| Audit files | `.github/ecosystems/codebase-context/audit/codebase-context-audit.md` |
| 品質観点 | export の有用性、signal-to-noise、pickup rule の順守、operator experience |
| 既定の export 挙動 | repository root の `CODEBASE_CONTEXT.md` を生成し、full filtered source code と useful supporting files を 1 つの markdown snapshot にまとめる |
| ユーザー override rule | include、exclude、source-only などの明示 pickup rule がある場合は、既定の broad export policy よりその指定を優先する |
| Runtime output | 生成された markdown snapshot は runtime output であり、manifest-owned install payload には含めない |
| Installed-target smoke | [tests/sandbox/run_codebase_context_container_smoke.sh](../../tests/sandbox/run_codebase_context_container_smoke.sh) が、共有の [tests/sandbox/base/Dockerfile](../../tests/sandbox/base/Dockerfile) から build した repo 同梱 Docker sandbox 内で installed-target smoke test を実行する。 |

### `repository-governance`

正本 manifest:
[.github/ecosystems/repository-governance/ECOSYSTEM.md](../../.github/ecosystems/repository-governance/ECOSYSTEM.md)

| 項目 | 現在の実装 |
|---|---|
| Root agent | [.github/agents/governance-repository-context-manager.agent.md](../../.github/agents/governance-repository-context-manager.agent.md) |
| Specialized agents | [.github/agents/governance-ecosystem-manifest.agent.md](../../.github/agents/governance-ecosystem-manifest.agent.md), [.github/agents/governance-ecosystem-delivery.agent.md](../../.github/agents/governance-ecosystem-delivery.agent.md) |
| Skills | [.github/skills/repository-governance-bootstrap/SKILL.md](../../.github/skills/repository-governance-bootstrap/SKILL.md), [.github/skills/repository-doc-governance/SKILL.md](../../.github/skills/repository-doc-governance/SKILL.md), [.github/skills/todo-progress-governance/SKILL.md](../../.github/skills/todo-progress-governance/SKILL.md) |
| Ownership contract | agents、skills、listed ecosystem-owned files、listed audit files、および manifest 自体 |
| Dependencies | `ecosystem-audit` |
| Ecosystem 固有 files | `.github/ecosystems/repository-governance/` 配下の template assets |
| Audit files | `.github/ecosystems/repository-governance/audit/repository-governance-audit.md` |
| Install portability rule | installable markdown 内の repository-local link は manifest-owned payload の内側で解決できなければならず、install 後の artifact は target repository 内で self-contained に保つ。 |
| 品質観点 | 文書の clarity、navigability、英日整合の質、operator usability |
| Audit flow | shared `ecosystem-audit` platform が shared core rules、shared work-quality rubric、この ecosystem の audit pack を on-demand で適用する |
| Installed-target smoke | [tests/sandbox/run_repository_governance_container_smoke.sh](../../tests/sandbox/run_repository_governance_container_smoke.sh) が、一時 repository へ ecosystem を install し、shipped bilingual template pack を適用したうえで、共有の [tests/sandbox/base/Dockerfile](../../tests/sandbox/base/Dockerfile) から build した repo 同梱 Docker sandbox 内で smoke test を実行する。 |

## CI

[.github/workflows/ci.yml](../../.github/workflows/ci.yml) が repository
validation 用の GitHub Actions entrypoint です。host runner 上で
`python -m pytest -q` の full suite を実行したあと、2 本の sandbox
container smoke runner も続けて実行します。

## 共有 Ecosystem Infrastructure

次のファイルは、ecosystem 全体を支える共有基盤であり、個別 ecosystem entry
ではありません。

| Path | 役割 |
|---|---|
| [.github/ecosystems/deliver_ecosystem.py](../../.github/ecosystems/deliver_ecosystem.py) | 宣言された dependency も含めて manifest-owned install/remove workflow を target `owner/repo` に適用し、PR ベース delivery を準備する。 |