# ADR-0004: macOS壁紙設定方式の選定

| 項目 | 内容 |
|------|------|
| ステータス | 承認済み |
| 日付 | 2026-04-01 |
| 意思決定者 | プロジェクトオーナー |

## コンテキスト

macOSのデスクトップ壁紙をプログラムから変更する方法は複数あり、macOSバージョンによって動作の安定性が異なる。

検討した選択肢:

- **AppleScript (System Events) 経由subprocess** — `osascript`コマンドでAppleScriptを実行し、System Eventsに壁紙変更を指示。
- **appscriptライブラリ** — PythonからFinderのdesktop_pictureを直接操作。古いライブラリで最新Pythonとの互換性に不安。
- **macos-wallpaper CLI** — sindresorhus製のNode.js CLIツール。macOS 10.14.4以降対応。
- **透明ウィンドウオーバーレイ** — 壁紙は変えず、最背面の透明ウィンドウに描画する方式。

## 決定

**AppleScript (System Events) 経由subprocessをメイン方式として採用する。** フォールバックとしてFinder経由のAppleScriptも実装する。

## 理由

- Pythonのsubprocess + osascriptはPython標準ライブラリのみで実現でき、外部依存がない
- System Events経由の壁紙設定はmacOS Monterey以降で安定して動作する
- appscriptはメンテナンスが停止しており、将来のPython/macOSバージョンで動作しなくなるリスクが高い
- macos-wallpaper CLIはNode.js依存が発生し、Pythonプロジェクトに不要な依存を追加することになる
- 透明ウィンドウ方式は「壁紙自体が天気で変わる」というコンセプトと合致しない

実装例:
```python
import subprocess

def set_wallpaper(image_path: str) -> bool:
    script = f'''
    tell application "System Events"
        tell every desktop
            set picture to "{image_path}"
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True)
    return result.returncode == 0
```

## 影響

- macOS Sequoia以降でSystem Events APIに変更があった場合、修正が必要になる可能性がある
- 全デスクトップ（マルチモニター含む）に同一壁紙を設定する設計とする
- Finder経由のフォールバック実装によりAppleScript方式の冗長性を確保する
