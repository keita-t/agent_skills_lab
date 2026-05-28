# プロジェクト憲章

この文書は、agent_skills_lab に固有の目的、用語、maintainer が明示した判断
だけを記録します。
既定では意図的に最小限のままにします。
明示指示がない限り、一般論の開発ルールや推測した方針を書き足しません。

## 推奨読書順

1. この文書: repository 固有の前提と明示された判断。
2. [docs/DOCUMENTATION_UPDATE_RULES.md](../DOCUMENTATION_UPDATE_RULES.md):
   docs 構成と英日同期の正本ルール。
3. [docs/TODO.md](../TODO.md): 現在の TODO と追跡メモ。
4. [docs/en/project-charter.md](../en/project-charter.md): 英語版の対応文書。

## 現在の憲章状態

- リポジトリの目的: agent_skills_lab は custom agents、skills、installable
  ecosystems の開発と実験のためのラボである。
- maintainer が明示した判断:
  - この repository は、再利用可能な ecosystem の source repository と、
    repository-governance を self-host する target repository の両方として
    運用する。
  - ecosystem operation と manifest governance は、それぞれ専用 agent の
    責務として分離していく。
  - ecosystem の install と remove は、shared script 中心ではなく
    agent-driven かつ PR-based な workflow へ寄せる。
  - manifest は ownership と dependency を表す structural contract へ縮小し、
    runtime や delivery 用 metadata は段階的に外していく。
  - legacy installer、updater、MCP runtime は削除し、delivery agent と
    manifest governance agent、および薄い helper module に置き換える。
- このファイルの編集ルール:
  - maintainer が明示的に示した、または承認した repository 固有の判断だけを
    追加する。

## Related Documents

- [docs/README.md](../README.md): ドキュメント案内と読書順。
- [docs/DOCUMENTATION_UPDATE_RULES.md](../DOCUMENTATION_UPDATE_RULES.md): docs
  ガバナンスと更新ポリシー。
- [docs/TODO.md](../TODO.md): 現在の TODO と追跡メモ。
- [docs/en/project-charter.md](../en/project-charter.md): 英語版の対応文書。
- [.github/ecosystems/README.md](../../.github/ecosystems/README.md):
  implementation-facing ecosystem index。