# toSong

テキストや資料から、ビジュアル生成・戯曲／MV台本・自由詩・Style設計・歌詞翻訳・マルチペルソナレビューを経て、Suno AI 用の楽曲一式を生成するエージェントスキル群と制作メソッドの公開リポジトリです。

## 収録スキル（`skills/`）

| スキル / 資料 | 役割 |
|---|---|
| [`skills/toSong/`](skills/toSong/SKILL.md) | テキストや資料から楽曲一式を組み立てる全8ステップのメインパイプライン |
| [`skills/toSong/references/story-guide.md`](skills/toSong/references/story-guide.md) | コンセプト・Visual & Sensory Bridge・戯曲／MV台本の設計ガイド |
| [`skills/toSong/references/lyrics-guide.md`](skills/toSong/references/lyrics-guide.md) | ワードマイニング・感情フィルター・自由詩・モーラ／譜割り・発音ガードのガイド |
| [`skills/toSong/references/Suno作曲メソッド.md`](skills/toSong/references/Suno作曲メソッド.md) | ペルソナ・作詞・メタタグ・Style／パラメータ設定の共通ルール集 |
| [`skills/genStyle/`](skills/genStyle/SKILL.md) | コンセプト・画像・台本から Suno AI の `Style of Music` / `Exclude Styles` を設計 |
| [`skills/song-review/`](skills/song-review/SKILL.md) | 作曲家・作詞家・AI作曲家（Suno専門家）の3視点で歌詞と Style をレビューし、普遍的知見をメソッドへ還元 |

## 制作パイプライン（`toSong`）

いきなり歌詞やタイトルを書かず、以下の順で映像・感情・音を立ち上げます。

1. **棚卸し・削ぎ落とし**：テーマ・感情軸を1つに絞り、曲調の軸を決める
2. **コンセプト ＆ 観客視点**：書き言葉で曲の狙いと聴後感を定義する
3. **ビジュアル生成**：キービジュアルを生成し、偶然の生活感・光の余白を残す
4. **Visual & Sensory Bridge**：画像から時間軸・五感・コア楽器・ペルソナを読み解く
5. **戯曲・MV台本（`script.md`）**：カメラ・環境音・ト書き・セリフの4層でシーンを組む
6. **ワードマイニング ＆ 自由詩（`poetry.md`）**：コア名詞を絞り、制約なしで詩を書く
7. **Style 設計（`genStyle`）**：空気感とコア楽器から `Style of Music` を組み立てる
8. **歌詞翻訳 ＆ タイトル命名**：譜割り・発音ガードを通して歌詞化し、最後にタイトルと一貫性を確定する（仕上げに `song-review` でブラッシュアップ）

## ディレクトリ構成

- `skills/` : 公開用スキル（`toSong`, `genStyle`, `song-review`）とガイド・メソッド文書
- `works/` : 制作した楽曲データ（歌詞・スタイル設定・台本・生成画像・Suno 公式共有リンクなど）

## 公開方針（Suno 音源の扱い）

- Suno Free プランで生成した楽曲は非商用利用限定のため、MP3 / WAV などの音声ファイル自体はリポジトリに同梱しません。
- 各作品フォルダ（`works/` 配下）では、歌詞・Style・制作過程データとあわせて **Suno の公式共有リンク（URL）** を掲載します。

## ライセンス

[MIT License](LICENSE)
