# 開発計画書: 天気連動壁紙チェンジャー

**Weather Wallpaper Changer**

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年4月1日 |
| バージョン | 1.0 |
| ステータス | ドラフト |

---

## 1. プロジェクト概要

本プロジェクトは、現在の天気情報に応じてmacOSのデスクトップ壁紙を自動的に切り替えるデスクトップアプリケーションを開発するものである。天気に合った画像をUnsplash APIから自動取得し、気温・天気・予報などのテキスト情報を壁紙にオーバーレイ描画し、ウィンドウの隙間からでも天気を確認できる体験を提供する。

| 項目 | 内容 |
|------|------|
| プロジェクト名 | 天気連動壁紙チェンジャー (Weather Wallpaper Changer) |
| 開発言語 | Python 3.10+ |
| 対象OS | macOS (Monterey 12.0以降) |
| ライセンス | MIT License (OSSとして公開予定) |

---

## 2. 機能要件

### 2.1 天気データ取得

複数のデータソースを組み合わせたハイブリッド構成で天気情報を取得する。

| データソース | 取得データ | 備考 |
|-------------|-----------|------|
| Open-Meteo API | 気温、天気コード、風速、湿度、降水確率、週間予報 | 無料・APIキー不要。メインデータソースとして使用 |
| Yahoo! YOLP API | 降水強度のリアルタイム予測 | APIキー要。雨雲情報の補完用 |
| Yahoo天気スクレイピング | 天気概況テキスト、週間天気詳細 | フォールバック用。サイト構造変更リスクあり |

### 2.2 壁紙画像取得

- Unsplash APIを使用し、天気条件に合致する高解像度の風景写真を自動検索・ダウンロード
- Unsplash無料プラン: 50リクエスト/時間。APIキー登録が必要
- 検索クエリは天気コードに応じてマッピング（例: 晴れ → "sunny sky landscape"、雨 → "rainy city"）
- 取得済み画像はローカルキャッシュし、同一天気での重複ダウンロードを防止
- 天気コードごとにデフォルト画像を同梱し、API到達不能時やオフライン環境でも動作するようにする

### 2.3 壁紙オーバーレイ描画

- Pillowライブラリを使用し、壁紙画像の上に天気情報テキストを描画
- 表示項目: 現在の気温、天気アイコン、天気概況、当日の最高/最低気温、降水確率
- 描画位置: 壁紙の右下隅（設定で変更可能）
- 半透明背景付きのテキストで視認性を確保
- フォント: Noto Sans JP Regular（NotoSansJP-Regular.ttf、単一ウェイトのみ）をリポジトリに同梱。フルセットは数十MBになるため、Regularのみに限定する

### 2.4 壁紙設定・更新ロジック

- macOSの壁紙設定はAppleScript (System Events) 経由subprocessで実行。フォールバックとしてFinder経由のAppleScriptも実装する
- 更新トリガー: 天気コードが変化したときのみ壁紙のベース画像を更新（無駄なAPIコールを抑制）
- オーバーレイ再描画: 天気コードが同一でも気温等が変化した場合はテキスト部分のみ再描画（ベース画像のダウンロードは行わない）
- 天気チェック間隔: 10分ごとにポーリング（前回の天気コードと比較）
- 前回状態の保持: 前回の天気コードおよび気温はメモリ内（変数）で保持する。ファイル永続化は行わない。プロセス再起動時は即座にAPIチェックし壁紙を設定する

---

## 3. システムアーキテクチャ

### 3.1 モジュール構成

| モジュール名 | 責務 |
|-------------|------|
| `main.py` | エントリポイント。スケジューラーとメインループの管理 |
| `weather_fetcher.py` | Open-Meteo API・YOLP APIからの天気データ取得、Yahoo天気スクレイピング |
| `image_fetcher.py` | Unsplash APIでの画像検索・ダウンロード、ローカルキャッシュ管理 |
| `wallpaper_renderer.py` | Pillowによる壁紙画像への天気情報オーバーレイ描画 |
| `wallpaper_setter.py` | macOSの壁紙設定（AppleScript経由subprocess） |
| `config.py` | 設定ファイルの読み込み・管理（YAML形式） |
| `weather_mapper.py` | 天気コードとUnsplash検索クエリ・アイコンのマッピング定義 |

### 3.2 ディレクトリ構成

```
weather-wallpaper-changer/
├── main.py
├── weather_fetcher.py
├── image_fetcher.py
├── wallpaper_renderer.py
├── wallpaper_setter.py
├── weather_mapper.py
├── config.py
├── config.yaml
├── requirements.txt
├── cache/                # 画像キャッシュ
├── defaults/             # 天気コードごとのデフォルト壁紙画像（API不通時のフォールバック）
├── fonts/                # オーバーレイ用フォント（NotoSansJP-Regular.ttf）
└── icons/                # 天気アイコン素材
```

### 3.3 データフロー

```
① main.py が10分間隔で weather_fetcher.py を呼び出し、現在の天気データを取得
        ↓
② 前回の天気コードと比較し、変化があれば image_fetcher.py で新しい壁紙画像を取得
        ↓
③ wallpaper_renderer.py が取得した画像に天気情報テキストをオーバーレイ描画
        ↓
④ wallpaper_setter.py が完成画像をmacOSのデスクトップ壁紙として設定
```

---

## 4. API仕様詳細

### 4.1 Open-Meteo API

| 項目 | 内容 |
|------|------|
| エンドポイント | `https://api.open-meteo.com/v1/forecast` |
| 認証 | 不要（完全無料） |
| レート制限 | 非商用: 10,000リクエスト/日 |
| 主要パラメータ | `latitude`, `longitude`, `current` (temperature_2m, weather_code, wind_speed_10m), `daily` (temperature_2m_max, temperature_2m_min, precipitation_probability_max), `timezone` |

リクエスト例:

```
https://api.open-meteo.com/v1/forecast?latitude=35.6762&longitude=139.6503&current=temperature_2m,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=Asia/Tokyo
```

### 4.2 Yahoo! YOLP 気象情報API

| 項目 | 内容 |
|------|------|
| エンドポイント | `https://map.yahooapis.jp/weather/V1/place` |
| 認証 | Yahoo! JAPAN APIキー（Client ID） |
| レート制限 | 50,000リクエスト/日/アプリ |
| 取得データ | 降水強度予測値（現在時刻から約60分後まで、10分間隔） |

### 4.3 Unsplash API

| 項目 | 内容 |
|------|------|
| エンドポイント | `https://api.unsplash.com/search/photos` |
| 認証 | Access Key（無料登録） |
| レート制限 | 無料枠: 50リクエスト/時間 |
| 主要パラメータ | `query`, `orientation=landscape`, `per_page=10` |

---

## 5. 天気コードマッピング

Open-MeteoのWMO天気コードをUnsplash検索クエリにマッピングする。以下は主要なマッピング定義である。

| コード | 天気 | 検索クエリ | アイコン |
|--------|------|-----------|---------|
| 0 | 快晴 | clear blue sky landscape | ☀️ |
| 1, 2, 3 | 晴れ/曇り | partly cloudy sky | ⛅ |
| 45, 48 | 霧 | foggy morning landscape | 🌫️ |
| 51, 53, 55 | 霧雨 | drizzle rain soft | 🌦️ |
| 61, 63, 65 | 雨 | rainy day city | 🌧️ |
| 71, 73, 75 | 雪 | snowy winter landscape | ❄️ |
| 80, 81, 82 | にわか雨 | rain shower dramatic sky | 🌧️ |
| 95, 96, 99 | 雷雨 | thunderstorm lightning | ⛈️ |

---

## 6. 設定ファイル仕様 (config.yaml)

ユーザーがカスタマイズ可能な設定項目をYAML形式で管理する。

```yaml
# 位置情報
location:
  latitude: 35.6762      # 緯度（デフォルト: 東京）
  longitude: 139.6503    # 経度（デフォルト: 東京）

# 更新設定
check_interval_min: 10   # 天気チェック間隔（分）

# オーバーレイ設定
overlay:
  position: bottom_right  # テキスト描画位置 (bottom_right / bottom_left / top_right / top_left)
  opacity: 0.7            # 背景の不透明度 (0.0〜1.0)
  font_size: 48           # 気温表示のフォントサイズ (px)

# APIキー
unsplash:
  access_key: "YOUR_UNSPLASH_ACCESS_KEY"

yahoo:
  client_id: ""           # 未設定時は降水予測無効

# キャッシュ設定
cache:
  max_images: 50          # キャッシュする画像の最大数
```

---

## 7. 依存ライブラリ

| ライブラリ | バージョン | 用途 |
|-----------|-----------|------|
| requests | >=2.28 | APIリクエスト、画像ダウンロード |
| Pillow | >=10.0 | 画像加工、テキストオーバーレイ描画 |
| beautifulsoup4 | >=4.12 | Yahoo天気スクレイピング |
| PyYAML | >=6.0 | 設定ファイル読み込み |
| schedule | >=1.2 | 定期実行スケジューラー |

---

## 8. セットアップ手順

1. Python 3.10+をインストール（未導入の場合: `brew install python@3.12` または `pyenv install 3.12`）
2. リポジトリをクローン: `git clone <repository-url>`
3. 依存ライブラリをインストール: `pip install -r requirements.txt`
4. Unsplash開発者アカウントでAPIキーを取得
5. （任意）Yahoo! JAPANデベロッパーネットワークでAPIキーを取得
6. `config.yaml`を編集し、APIキーと位置情報を設定
7. 実行: `python main.py`（バックグラウンド実行: `nohup python main.py &`）

---

## 9. 今後の拡張案

- launchdでmacOSログイン時自動起動対応
- 時間帯に応じた壁紙の雰囲気変更（朝焼け、夜景など）
- 雨の日のアニメーションエフェクト（透明ウィンドウオーバーレイ）
- メニューバーアイコンでの天気確認機能追加
- ユーザー独自の壁紙画像フォルダ対応（Unsplash不使用モード）
- AI画像生成による天気壁紙の自動生成
- Windows / Linuxクロスプラットフォーム対応

---

## 10. リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| Unsplash APIレート制限到達 | 新しい壁紙画像が取得できない | キャッシュ活用、前回の壁紙を維持 |
| Yahoo天気のサイト構造変更 | スクレイピング失敗 | Open-Meteoデータのみでフォールバック動作 |
| macOSアップデートで壁紙設定API変更 | 壁紙が切り替わらない | AppleScript / osascript両方のフォールバック実装 |
| ネットワーク接続なし | API呼び出し失敗 | キャッシュ済みの壁紙を使用、リトライ制御 |
