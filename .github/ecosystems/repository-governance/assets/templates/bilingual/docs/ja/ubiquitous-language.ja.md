# ユビキタス言語

この文書は、この repository で maintainer と agent が文脈をそろえるために
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
| プロジェクト憲章 | repository 固有の前提と maintainer の明示判断を最小限で記録する文書。 |
| ユビキタス言語 | 方針文書ではなく、文脈合わせのために保つ共有語彙レイヤー。 |
| 文書更新ルール | stable docs 更新の正本ルール。 |
| ドキュメント案内 | 人間と agent を正本文書へ案内する reader-facing index。 |
| operational backlog | `docs/TODO.md` に集約する現在の TODO と追跡メモ。 |

## Related Documents

- [docs/ja/project-charter.ja.md](./project-charter.ja.md): repository 固有の
  前提と maintainer の明示判断。
- [docs/DOCUMENTATION_UPDATE_RULES.md](../DOCUMENTATION_UPDATE_RULES.md): stable
  docs 更新の正本ルール。
- [docs/en/ubiquitous-language.md](../en/ubiquitous-language.md): 英語版の対応
  文書。