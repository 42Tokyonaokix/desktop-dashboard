# Desktop Dashboard

macOS のデスクトップ壁紙に天気・タスク・励ましコメントを表示するダッシュボードアプリ。

Obsidian vault のタスクファイルと連携し、壁紙を見るだけで今日やるべきことが把握できる。

## 機能

- **天気表示** — Open-Meteo API から現在の天気・気温・降水確率を取得して壁紙に表示
- **タスク表示** — Obsidian vault のタスクファイル（YAML frontmatter）を読み取り、`status: todo` + `priority: high` のタスクを壁紙に一覧表示
- **励ましコメント** — vault 内のコメントファイルを読み取って壁紙下部に表示
- **設定ダッシュボード** — Dock アイコンクリックで設定画面を開き、表示内容やレイアウトをGUIで変更
- **タスク編集** — 設定画面内のエディタで vault のタスクファイルを直接編集・保存
- **Dock アイコン** — 天気情報＋タスク件数バッジを Dock アイコンに表示

## 壁紙レイアウト

壁紙の中央 1500x1000 の領域に3つの半透明カードを縦に配置：

```
┌─────────────────────────┐
│   ☀️ 22.5°C             │  ← 天気セクション
│   快晴  最高28°/最低18°  │
├─────────────────────────┤
│   📋 Tasks              │  ← タスクセクション
│   ● Task 1   #dev       │
│   ● Task 2   #bug       │
│   ...                   │
├─────────────────────────┤
│   💬 Today              │  ← 励ましコメント
│   最近はこんなことを...   │
└─────────────────────────┘
```

## 必要環境

- macOS
- Python 3.9+
- Unsplash API キー（壁紙背景画像の取得用、無料）

## セットアップ

```bash
# 依存インストール
pip3 install -r requirements.txt

# 設定ファイルを作成
cp config.example.yaml config.yaml
```

`config.yaml` を編集：

```yaml
# Unsplash API キーを設定（https://unsplash.com/developers で無料取得）
unsplash:
  access_key: "YOUR_API_KEY"

# Obsidian vault のパスを設定
obsidian:
  vault_dir: "/path/to/your/obsidian-vault"
  motivation_file: "/path/to/your/obsidian-vault/dashboard/motivation.md"
```

## 使い方

### GUI モード（デフォルト）

```bash
python3 src/main.py
```

- Dock にアイコンが表示される（天気 + タスク数バッジ）
- Dock アイコンをクリックで設定ダッシュボードを表示
- 壁紙は天気10分 / タスク5分の間隔で自動更新

### ヘッドレスモード

```bash
python3 src/main.py --headless
```

GUI なしでバックグラウンド動作。

## 設定ダッシュボード

Dock アイコンクリックで開く設定画面では以下の操作が可能：

| タブ | 操作内容 |
|------|---------|
| 表示設定 | セクションの表示ON/OFF、順序変更、サイズ比率、カード透明度、フォントサイズ |
| Vault設定 | タスク参照ディレクトリ、励ましコメントファイル、タスク表示件数 |
| タスク管理 | vault のタスクファイル一覧表示、テキストエディタで内容を編集・保存 |

設定変更は「保存」ボタンで `config.yaml` に永続化される。「即時更新」ボタンで壁紙をその場で再描画。

## 設定項目（config.yaml）

```yaml
location:
  latitude: 35.6762      # 緯度
  longitude: 139.6503    # 経度

weather:
  check_interval_min: 10 # 天気の更新間隔（分）

unsplash:
  access_key: ""         # Unsplash API キー

obsidian:
  vault_dir: ""               # Obsidian vault のパス
  check_interval_min: 5       # タスク・コメントの更新間隔（分）
  tasks:
    max_items: 8              # 壁紙に表示するタスク数
    status: "todo"            # フィルタ: status
    priority: "high"          # フィルタ: priority
  motivation_file: ""         # 励ましコメントファイルのパス

dashboard:
  width: 1500                 # ダッシュボード領域の幅 (px)
  height: 1000                # ダッシュボード領域の高さ (px)
  sections:                   # 表示セクション（順序変更可）
    - weather
    - tasks
    - motivation
  section_weights: [30, 40, 30]  # セクションの高さ比率
  card_opacity: 0.6           # カードの透明度 (0.0-1.0)
  font_size: 36               # フォントサイズ
```

## タスクファイルのフォーマット

Obsidian vault 内のタスクファイルは以下の YAML frontmatter 形式に対応：

```markdown
---
title: "タスクのタイトル"
status: todo          # todo / in_progress / done
priority: high        # high / medium / low
progress: 0/3
tags: [dev, feature]
---

## 内容
タスクの詳細...
```

## プロジェクト構成

```
src/
├── domain/                     # データ取得・ロジック
│   ├── models.py               # 共有データクラス
│   ├── weather_fetcher.py      # Open-Meteo API
│   ├── weather_mapper.py       # WMO コードマッピング
│   ├── task_reader.py          # vault タスク読み取り
│   └── motivation_reader.py    # 励ましコメント読み取り
├── infra/                      # 表示・OS連携
│   ├── wallpaper_renderer.py   # 3セクション壁紙描画
│   ├── wallpaper_setter.py     # macOS 壁紙設定
│   ├── image_fetcher.py        # Unsplash 画像取得
│   ├── dock_icon.py            # Dock アイコン生成
│   └── settings_window.py      # 設定ダッシュボード UI
├── config.py                   # 設定ローダー
└── main.py                     # オーケストレーター
```

## テスト

```bash
python3 -m pytest -v
```

## ライセンス

MIT
