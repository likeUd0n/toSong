# toSong

**toSong は、音楽生成 AI「Suno AI」に入力するための『歌詞・Style プロンプト・パラメータ一式』を、思いつきや手元の資料から自動で組み立てる AI エージェント向けスキル群（Suno 専用プロンプター／制作ワークフロー）です。**

※ このリポジトリ自体は音声ファイル（MP3/WAV）を直接生成しません。Suno の **Custom Mode** にそのままコピペして「Create」を押すだけの状態を作るための設計・プロンプト生成ツールです。

---

## 出力ファイルと Suno への貼り付け方

制作が完了すると、曲フォルダの直下に **Suno 貼り付け用ファイル**、その中の `work/` に **制作過程の資料（台本・自由詩・画像・ペルソナ等）** が出力されます。

Suno に貼り付けるときは、お使いのプランに合わせて以下をコピーしてください（`suno-paste.md` がある曲では、1 つのファイル内のコードブロックからまとめてコピーできます）。

### 1. 無料プラン（Free）で使うファイル
まずはこの **3 つだけ** を Suno の Custom Mode に貼り付ければ曲を作れます。

| ファイル | Suno 画面の貼り付け先 | 内容 |
|---|---|---|
| `title.txt` | **Title** | 曲タイトル |
| `style.txt` | **Style of Music** | ジャンル・楽器・声質・テンポなどの英語タグ |
| `lyrics.txt` | **Lyrics** | `[Verse]` などのメタタグ付き歌詞（ひらがな・発音調整済み） |

### 2. 有料プラン（Pro / Premier）で追加するファイル
有料プランでは、上記 3 つに加えて詳細コントロール用の項目も使えます。

| ファイル | Suno 画面の貼り付け先 / 設定箇所 | 内容 |
|---|---|---|
| `exclude.txt` | **Exclude Styles** | 除外したい楽器・要素（※無料プランでは欄がないため不要） |
| `settings.txt` | **Style Influence / Weirdness** 等 | Custom Mode のオンオフや各スライダーの推奨値（`%`） |

### 3. 貼り付けないファイル（`work/` フォルダ）
- `script.md`（戯曲・MV台本）、`poetry.md`（自由詩）、`ペルソナ.md`、`styles.txt`（設計メモ）、`visual_*.jpg`（キービジュアル）などが入ります。Suno への貼り付けは不要です。

---

## 収録作品（`works/`）

| リボンが揺れたらメリークリスマス | ひだまりの角を曲がったら | 水たまりが光を返すまで |
| :---: | :---: | :---: |
| <a href="https://suno.com/s/VSih94sZPmDFpYhC"><img src="works/リボンが揺れたらメリークリスマス/work/visual_1.jpg" width="240" alt="リボンが揺れたらメリークリスマス"></a> | <a href="https://suno.com/s/POwGnHGp9N4mFbet"><img src="works/ひだまりの角を曲がったら/work/visual_1.jpg" width="240" alt="ひだまりの角を曲がったら"></a> | <a href="https://suno.com/s/z7HarBUlpCsb0QOg"><img src="works/水たまりが光を返すまで/cover.jpg" width="240" alt="水たまりが光を返すまで"></a> |
| [![Listen on Suno](https://img.shields.io/badge/%E2%96%B6%20Listen%20on-Suno-ff4b2b?style=flat-square)](https://suno.com/s/VSih94sZPmDFpYhC) | [![Listen on Suno](https://img.shields.io/badge/%E2%96%B6%20Listen%20on-Suno-ff4b2b?style=flat-square)](https://suno.com/s/POwGnHGp9N4mFbet) | [![Listen on Suno](https://img.shields.io/badge/%E2%96%B6%20Listen%20on-Suno-ff4b2b?style=flat-square)](https://suno.com/s/z7HarBUlpCsb0QOg) |
| [作品データ](works/リボンが揺れたらメリークリスマス/) | [作品データ](works/ひだまりの角を曲がったら/) | [作品データ](works/水たまりが光を返すまで/) |

> GitHub の Markdown 仕様上、外部オーディオプレイヤー（`<iframe>` 等）の直接埋め込みは非対応のため、ジャケット画像・再生バッジから Suno 公式ページへリンクしています。

---

## 収録スキル（`skills/`）

| スキル / 資料 | 役割 |
|---|---|
| [`skills/toSong/`](skills/toSong/SKILL.md) | テキストや資料から楽曲一式を組み立てる全8ステップのメインパイプライン |
| [`skills/toSong/references/story-guide.md`](skills/toSong/references/story-guide.md) | 観察・連想メモ、戯曲／MV台本、コンセプト・ペルソナ確定の設計ガイド |
| [`skills/toSong/references/lyrics-guide.md`](skills/toSong/references/lyrics-guide.md) | ワードマイニング・感情フィルター・自由詩・モーラ／譜割り・発音ガードのガイド |
| [`skills/toSong/references/Suno作曲メソッド.md`](skills/toSong/references/Suno作曲メソッド.md) | ペルソナ・作詞・メタタグ・Style／パラメータ設定の共通ルール集 |
| [`skills/genStyle/`](skills/genStyle/SKILL.md) | コンセプト・画像・台本から Suno AI の `Style of Music` / `Exclude Styles` を設計 |
| [`skills/song-review/`](skills/song-review/SKILL.md) | 作曲家・作詞家・AI作曲家（Suno専門家）の3視点で歌詞と Style をレビューし、普遍的知見をメソッドへ還元 |

## 制作パイプライン（`toSong`）

いきなり歌詞やタイトルを書かず、以下の順で映像・感情・音を立ち上げます。

1. **棚卸し・削ぎ落とし【還元】**：情報や結論を手放して感情の種を1つに絞り、曲調の軸を決める
2. **ビジュアル生成【攪拌】**：キービジュアルを生成し、偶然の生活感・光の余白を残す
3. **観察 ＆ 連想メモ【絶縁】**：画像に写った事実と連想の種だけを拾い、元テキストの重力を断つ
4. **戯曲・MV台本（`script.md`）【実験】**：設定を固める前にカメラ・環境音・ト書き・セリフの4層でキャラを動かす
5. **設計の確定（`concept.md` / `ペルソナ.md`）【結晶】**：台本から立ち上がったコンセプト・観客視点・五感・コア楽器・ペルソナを確定する
6. **ワードマイニング ＆ 自由詩（`poetry.md`）**：コア名詞を絞り、制約なしで詩を書く
7. **Style 設計（`genStyle`）**：空気感とコア楽器から `Style of Music` を組み立てる
8. **歌詞翻訳 ＆ タイトル命名**：譜割り・発音ガードを通して歌詞化し、最後にタイトルと一貫性を確定する（仕上げに `song-review` でブラッシュアップ）

## ディレクトリ構成

- `skills/` : 公開用スキル（`toSong`, `genStyle`, `song-review`）とガイド・メソッド文書
- `works/` : 制作した楽曲データ（Suno 貼り付け用テキスト・制作過程データ・Suno 公式共有リンクなど）

## 公開方針（Suno 音源の扱い）

- Suno Free プランで生成した楽曲は非商用利用限定のため、MP3 / WAV などの音声ファイル自体はリポジトリに同梱しません。
- 各作品フォルダ（`works/` 配下）では、歌詞・Style・制作過程データとあわせて **Suno の公式共有リンク（URL）** を掲載します。

## ライセンス

[MIT License](LICENSE)
