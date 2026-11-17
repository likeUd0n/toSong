# toSong

![Status: WIP](https://img.shields.io/badge/status-WIP%20%2F%20%E9%96%8B%E7%99%BA%E4%B8%AD-orange?style=flat-square)

> [!NOTE]
> このプロジェクトは現在**開発中（実験段階）**です。スキル構成・手順・出力形式は予告なく変更されることがあります。
>
> **現在の課題**
> - 生成時間が長くなる（テストで実験したところ約 10 分かかった）
> - 歌詞の意味がまだ自然ではない

**toSong は、音楽生成 AI「Suno AI」に入力するための『歌詞・Style プロンプト・パラメータ一式』を、思いつきや手元の資料から自動で組み立てる AI エージェント向けスキル群（Suno 専用プロンプター／制作ワークフロー）です。**

※ このリポジトリ自体は音声ファイル（MP3/WAV）を直接生成しません。Suno の **Custom Mode** にそのままコピペして「Create」を押すだけの状態を作るための設計・プロンプト生成ツールです。

## デモ：雑談のお題が 1 曲になるまで

<a href="docs/demo.mp4"><img src="docs/demo.gif" width="720" alt="toSong デモ：雑談でお題 → /toSong に貼る → Suno に貼って Create"></a>

| Before | Process | After |
| :--- | :--- | :--- |
| AI との雑談で出たお題 | `/toSong` に貼っておまかせで歌詞・Style・ジャケットを生成し、`suno-paste.md` を Suno（無料プラン）に貼って Create | 『三コマ目のドアノブ』 [![Listen on Suno](https://img.shields.io/badge/%E2%96%B6%20Listen%20on-Suno-ff4b2b?style=flat-square)](https://suno.com/s/ACwcZl4hpqH89E9g) |

※ GIF は無音です（リンク先の MP4 は BGM 付き、曲本編は Suno のリンクから聴けます）。

---

## 必要なもの

- **スキル対応の AI コーディングエージェント**：`SKILL.md` 形式を読み込めるツール（Claude Code、Antigravity、OpenCode など）
- **Python 3**：`skills/toSong/scripts/pick_motifs.py`（ステップ 2 のランダム抽選）の実行に使用（標準ライブラリのみで動作するため追加パッケージは不要）
- **Suno AI アカウント**：出力された歌詞・Style を Custom Mode に貼り付けて楽曲を生成するため（Free / Pro / Premier いずれも対応）
- **画像生成手段**（任意）：発想モードのステップ 1 でキービジュアルを生成する場合に使用（`cf-image` 等の画像生成 MCP ツール、Antigravity の `image-generator` サブエージェント、または外部の画像生成ツール。文脈ベースや画像なしで進める場合は不要）

## インストール方法

1. リポジトリを取得します。
   ```bash
   git clone https://github.com/likeUdonThanRamen/toSong.git
   ```
2. `skills/` 配下の 3 フォルダ（`toSong`, `genStyle`, `song-review`）を、お使いの AI エージェントのスキルディレクトリへコピー（または配置）します。
   - **Claude Code**：`~/.claude/skills/`（またはプロジェクトの `.claude/skills/`）
   - **Antigravity**：`~/.gemini/config/skills/`（またはワークスペースのスキルディレクトリ）
3. AI エージェント上で「`/toSong`」や「この資料から曲を作って」と指示して開始します。

---

## 出力ファイルと Suno への貼り付け方

制作が完了すると、曲フォルダの直下には **Suno 貼り付け用ファイル（`suno-paste.md` / `suno-paste.html`）** と **ジャケット画像（`cover.jpg`）** のみが出力されます。単体テキストや制作過程の資料はすべて `work/` サブフォルダに格納されます。

Suno に貼り付けるときは、ブラウザで `suno-paste.html` を開いて各「コピー」ボタンを押すか、`suno-paste.md` 内の各コードブロックを上から順（Lyrics → Style of Music → Title）にコピーしてください。

### 1. 曲フォルダ直下（ルート）
| ファイル | 内容 |
|---|---|
| `suno-paste.html` | ブラウザで開いてワンクリックでコピーできる貼り付け用ページ（Suno Custom Mode 順：Lyrics → Style of Music → Title） |
| `suno-paste.md` | Suno の Custom Mode にそのまま貼れるコードブロック集（上から Lyrics → Style of Music → Title、有料プラン時は Exclude Styles / パラメータも収録） |
| `cover.jpg` | 曲タイトルと空気感に合わせたジャケット画像（画像生成を有効にしている場合） |

### 2. `work/` サブフォルダ（単体テキスト・制作過程の資料）
- 単体ファイル：`title.txt`, `style.txt`, `lyrics.txt`（有料プラン時は `exclude.txt`, `settings.txt` も生成）
- 制作資料：`script.md`（戯曲・MV台本）、`poetry.md`（自由詩）、`ペルソナ.md`、`styles.txt`（設計メモ）、`visual_*.jpg`（キービジュアル）、`review.md` 等

---

## 収録作品（`works/`）

| 三コマ目のドアノブ | とりあえず起きてから |
| :---: | :---: |
| <a href="https://suno.com/s/ACwcZl4hpqH89E9g"><img src="works/三コマ目のドアノブ/cover.jpg" width="240" alt="三コマ目のドアノブ"></a> | <a href="https://suno.com/s/K1M5T7TxHk4mC457"><img src="works/とりあえず起きてから/cover.jpg" width="240" alt="とりあえず起きてから"></a> |
| [![Listen on Suno](https://img.shields.io/badge/%E2%96%B6%20Listen%20on-Suno-ff4b2b?style=flat-square)](https://suno.com/s/ACwcZl4hpqH89E9g) | [![Listen on Suno](https://img.shields.io/badge/%E2%96%B6%20Listen%20on-Suno-ff4b2b?style=flat-square)](https://suno.com/s/K1M5T7TxHk4mC457) |
| [作品データ](works/三コマ目のドアノブ/) | [作品データ](works/とりあえず起きてから/) |

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
