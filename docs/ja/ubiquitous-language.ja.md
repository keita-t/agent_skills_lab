# ユビキタス言語

この文書は、agent_skills_lab で maintainer と agent が文脈をそろえるために
使う共有語彙を記録します。
プロジェクト憲章とは異なり、このファイルは現在の repository の挙動、現行
docs、manifest、workflow に根拠がある限り agent が更新できます。
ただし、この文書を使って方針、maintainer の判断、推測したローカルルールを
増やしてはいけません。repository の scope や policy を変える内容は、
maintainer が明示的に憲章編集を指示した場合にのみ憲章へ反映します。

## 編集ルール

- agent は、この repository で現に使われている用語が実装、docs、manifest、
  agent 名、skill 名、または運用 workflow に現れているときに、その用語を
  追加または更新できる。
- agent は、この文書を approval requirement、隠れたローカルルール、推測の
  taxonomy を作る場所として使ってはならない。
- 各項目は記述的かつ現行状態に保つ。基盤となる概念が使われなくなったら削除
  または改稿する。
- ある用語が repository 固有の scope や maintainer の明示判断を含む場合は、
  maintainer が明示的に指示したときだけ憲章へ記録する。

## 現在の語彙

| 用語 | この repository における意味 |
|---|---|
| agent_skills_lab | custom agents、skills、installable ecosystems の開発と実験のためのラボ。 |
| ecosystem | manifest が ownership を持つ agent、skill、helper file をひとまとまりで target repository に届ける再利用可能なパッケージ。 |
| manifest | `.github/ecosystems/<slug>/ECOSYSTEM.md` にある、ecosystem の ownership、dependency、install payload を定義する Markdown contract。 |
| ownership contract | install と remove の対象として manifest が所有を宣言するファイル集合。 |
| installed runtime contract | ownership を増やさずに、install 済み ecosystem が target repository 上でどう実行されるかを記述する optional な manifest metadata。 |
| runtime launcher | installed runtime を宣言した ecosystem で、operator が target repository から起動する manifest-owned entrypoint。 |
| runtime container | shared installed runtime contract を通じて起動され、target repository 上の install 済み behavior を実行する disposable container。 |
| audit-files | shared audit platform を各 ecosystem から拡張するために manifest で宣言する ecosystem 固有の audit 文書。所有権はその ecosystem が持つ。 |
| ecosystem-audit | 共通 audit agent、cross-ecosystem な core rules、audit report contract を提供する shared ecosystem。 |
| work-quality audit | structural conformance だけでなく、成果物の質と振る舞い品質のシグナルも評価する監査レイヤー。 |
| rubric summary | 品質次元、rating、evidence basis、confidence を detailed finding より先に要約する audit section。 |
| evidence basis | finding が artifact-observed、runtime-observed、definition-inferred のどれに基づくかを示すラベル。 |
| upstream improvement feedback | local repair だけでなく、source ecosystem 側へ返す改善提案。 |
| sandbox smoke | install 済み ecosystem の挙動を検証するための repo 同梱 Docker workflow。runtime-free ecosystem は sandbox container 内で完結でき、runtime-enabled ecosystem は install 済み runtime launcher を流用して runtime container を唯一の実行境界として使う。 |
| source repository | reusable ecosystem asset を authoring し、delivery 前に監査する側の repository。 |
| target repository | ecosystem の manifest-owned payload を install または remove workflow で受け取る側の repository。 |
| repository-governance | repository docs、更新ルール、template、audit guidance、関連オーケストレーション guidance を扱う ecosystem。 |
| ユビキタス言語 | 方針文書ではなく、maintainer と agent の文脈合わせを助ける共有語彙レイヤー。 |

## Related Documents

- [docs/ja/project-charter.ja.md](./project-charter.ja.md): repository 固有の
  前提と maintainer の明示判断。
- [docs/DOCUMENTATION_UPDATE_RULES.md](../DOCUMENTATION_UPDATE_RULES.md): stable
  docs 更新の正本ルール。
- [docs/en/ubiquitous-language.md](../en/ubiquitous-language.md): 英語版の対応
  文書。