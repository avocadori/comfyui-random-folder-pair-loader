# Random Folder Pair Loader for ComfyUI

親フォルダ直下に大量にある **子フォルダ** を **ランダム順で 1 回ずつ巡回**し、
各フォルダに格納された **画像ファイル + 音声ファイル** を 1 組だけ取り出して ComfyUI ワークフローへ渡すカスタムノードです。

---

## 1. 特徴

| 機能               | 説明                                                                        |
| ---------------- | ------------------------------------------------------------------------- |
| **フォルダ単位シャッフル**  | 子フォルダを重複なくランダム抽選し、一巡したら停止します。                                             |
| **多拡張子対応**       | 画像: `png / jpg / jpeg / bmp / webp`<br>音声: `mp4 / wav / m4a / flac / aac` |
| **同名ファイル優先ロジック** | `sample.jpg` + `sample.wav` のように *ベース名* が一致する組み合わせを自動選択（設定で無効化可）。         |
| **ワンクリック再シャッフル** | `reset_cycle` パラメータを `True` にすると直ちに再抽選して再実行。                              |
| **標準型で出力**       | 出力型は `"IMAGE"` / `"AUDIO"` なので追加変換なしで既存ノードに接続可能。                          |

---

## 2. 動作要件

* ComfyUI (2024‑12‑20 以降推奨)
* Python 3.10+
* PyTorch + torchaudio
* Pillow

インストール例（CUDA 12.1 環境）

```bash
pip install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
pip install pillow
```

---

## 3. インストール手順

```bash
# ComfyUI の custom_nodes 配下へクローン
cd /path/to/ComfyUI/custom_nodes

git clone https://github.com/yourname/random_folder_pair_loader.git
# ZIP ダウンロード → 展開でも可
```

フォルダ構成

```
random_folder_pair_loader/
├─ __init__.py
├─ nodes.py
└─ README.md  ← このファイル
```

ComfyUI を再起動すると、ノード検索で
`file/io → ランダム子フォルダ (画像+音声)` が追加されます。

---

## 4. ノードパラメータ

| パラメータ             | 型 / 既定値                | 説明                                                  |
| ----------------- | ---------------------- | --------------------------------------------------- |
| **root\_dir**     | `STRING` / `./dataset` | 親フォルダのパス。                                           |
| **shuffle\_seed** | `INT` / `0`            | 0=毎回ランダム。固定値で順序を再現。                                 |
| **pair\_mode**    | `ENUM` / `same_name`   | `same_name` : 同名ファイル優先<br>`first` : フォルダ内先頭ファイルを使用。 |
| **reset\_cycle**  | `BOOLEAN` / `False`    | True にするとキャッシュを破棄し、初期状態から再巡回。                       |

---

## 5. 対応フォルダレイアウト例

```
dataset/
├─ 00001/
│   ├─ 00001.jpg
│   └─ 00001.wav
├─ 00002/
│   ├─ picture.png
│   └─ voice.m4a
└─ ...
```

---

## 6. 典型的なワークフロー例

```
Random Folder Pair ─▶  CLIP Vision Encode ─▶  ...
                   └▶  Audio Latent Encode ─▶ ...
```

* 一巡が終わると `StopIteration` が発生し、Queue が空になって自動停止。
* もう一周したい場合は `reset_cycle` を **ON** にして再実行してください。

---

## 7. 既知の問題 / よくある質問

| 質問・症状                           | 回答                                                            |
| ------------------------------- | ------------------------------------------------------------- |
| **mp4 → Tensor 変換が遅い**          | 軽量な `wav` や `m4a` へ変換しておくと高速です。                               |
| **子フォルダにペアがないとエラー**             | 例外を投げてワークフローを停止します。ペアを必ず用意してください。                             |
| **StopIteration を UI に表示したくない** | `nodes.py` を改造し、`BOOLEAN` 出力で end flag を返して条件分岐ノードへ渡す方法があります。 |

---

## 8. ライセンス

MIT © 2025 YourName

---

## 9. 更新履歴

| 日付         | 版     | 主な変更点                      |
| ---------- | ----- | -------------------------- |
| 2025‑05‑29 | 1.0.0 | 初版公開（多拡張子サポート、同名ペア優先ロジック）。 |
