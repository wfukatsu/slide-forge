# Slides — スライド作成スキルパッケージ

Google Slides を Claude Code から生成するためのスキル群と、その成果物・実例をまとめた
ワークスペース。スキルの実体は `skills/` にあり、`~/.claude/skills/` からシンボリック
リンクで参照される(リンクの張り直しは下記セットアップ参照)。

## 構成

| パス | 内容 |
|------|------|
| `skills/google-slides/` | コンポーザー方式の Google Slides 生成(36 スライドタイプ・インフォグラフィクス・構成図) |
| `skills/google-slides-template/` | テンプレート(マスター)複製方式の生成。scalar-2026 等のテンプレート登録・デッキ生成・視覚 QA |
| `skills/scalar-product-slides/` | Scalar 会社紹介・製品/機能紹介・ユースケース資料の専用ワークフロー(上 2 つの上に載る) |
| `scalar-intro-2026/` | 2026-08 作成の Scalar 紹介資料の生成スクリプトと調査メモ(実例) |
| `CLAUDE.md` | このワークスペースでの Claude Code 向け指示 |

## セットアップ(新しい環境で使う場合)

```bash
# 1. スキルをシンボリックリンクで登録
for s in google-slides google-slides-template scalar-product-slides; do
  ln -s "$(pwd)/skills/$s" ~/.claude/skills/$s
done

# 2. 共有 venv(2 スキルで共用)
python3 -m venv ~/.claude/venvs/gslides
~/.claude/venvs/gslides/bin/pip install -U -r skills/google-slides/requirements.txt
for s in google-slides google-slides-template; do
  ln -sfn ~/.claude/venvs/gslides skills/$s/.venv
done

# 3. OAuth 認証情報(コミット対象外)を配置
#    Google Cloud Console で OAuth デスクトップクライアントを作成し
#    Slides API / Drive API を有効化して skills/google-slides/config/credentials.json に置く

# 4. クラウド公式アイコン(再配布不可のためコミット対象外)を取り込む
skills/google-slides-template/.venv/bin/python \
  skills/google-slides-template/scripts/fetch-cloud-icons.py
```

## コミットしないもの(.gitignore)

- OAuth の `credentials.json` / `token.json`(秘密情報)
- AWS / Google Cloud / Azure の公式アイコン実体(各社の資産のため再配布しない)
- venv・生成物・キャッシュ・Slidev 学習プロジェクト(`*-study-template/` ほか)
