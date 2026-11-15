---
name: genStyle
description: 物語・コンセプト・ビジュアルイメージ・コア楽器から、Suno AI 用の Style of Music / Exclude Styles / 各種パラメータ（styles.txt）を生成・最適化する。「スタイルを作って」「SunoのStyleを考えて」「/genStyle」と頼まれたとき、または toSong スキルから呼び出されたときに使う。
---

# Suno Style 生成（genStyle）

曲のコンセプト・感情トーン・ビジュアルの空気感から、Suno AI が意図通りに解釈できる `styles.txt` を設計する。

## Suno の解釈メカニズム（前提知識）
- **確率的重み付けモデル**：Suno は文章を順番に実行する DAW ではなく、Style 欄全体を「音楽クラスタの確率的重み付け」として一括解釈する。矛盾する形容詞や過剰なタグ（6個以上）を並べるほど平均化・破綻しやすい。
- **音楽理論の効き方**：
  - **Key（調性）**（`C major`, `A minor` 等）：非常に有効。そのスケールに属する音・コード進行へ確率を寄せる。
  - **BPM / 拍子**（`175 BPM`, `4/4 time`, `3/4 waltz`, `half-time feel`）：ドラム・ベース・ボーカルのリズムグリッドを強力に固定する。
  - **コード進行の指定**：`ii-V-I` のようなローマ数字やコード譜の直書きは楽器譜として読めないため不安定。代わりに **`jazzy chords`, `suspended chords`, `lush voicings`, `power chords`, `arpeggiated synth pads`** など「和声の質感（Harmonic Texture）」を表す英語形容詞を使う。

## 参照する共通メソッド
- `references/Suno作曲メソッド.md`（存在する場合、最新の制約・推奨値を優先して従う）

---

## 手順

### 1. 入力情報の整理
以下の要素を確認する（不足している場合は、与えられた物語・テキスト・画像から妥当な値を補う）：
- **曲のコンセプト・ギャップ**：歌詞のテーマと曲調の関係（例：暗い歌詞 × 底なしに明るいポップ、あるいはストレートな叙情系）
- **ターゲットの雰囲気・色**：ビジュアル画像や情景から読み取れる質感（例：冬の透明感、夜のネオン、午後の木漏れ日）
- **ボーカル・ペルソナ**：性別、声質（例：透明感と儚さのある明るい女性ボーカル、力強い少年声など）
- **コア楽器（3〜4点）**：全編を通して曲の軸になる楽器

### 2. Style of Music の組み立て（語順と情報密度が命）
Suno は **先頭 20〜30 語に最も強い重み** を置くため、必ず以下の順で英語キーワードを並べる。

1. **ジャンル / サブジャンル**（例：`Hyper-cheerful J-Pop, Vocaloid-inspired Idol Pop`）
2. **声質 / 歌唱スタイル**（例：`Bright Cute Female Vocal, Clear Transparent Female Vocal` ※ `Fragile` 等の弱さを表す形容詞は音圧低下を招くため避ける）
3. **テーマ感 / BPM / 拍子 / Key**（例：`175 BPM, 4/4 time, Bright Major Key` または `E minor`）
4. **コア楽器（3〜4点に絞る）**（例：`Sparkling Piano, Celesta, Sleigh Bells, Tight Snappy Drums` ※ `Lush Voicings` 等の中低域を濁らせる語は避ける。静と動のメリハリをつけたい曲では、全編疾走させる `Driving` のような修飾語を外す）
5. **全体の質感・プロダクション**（例：`Dynamic Contrast, Crisp Modern Production, High-Energy Chorus` ※ 静と動の落差を出したい場合は `Dynamic Contrast` を必ず含める）

> [!CAUTION]
> **避けるべきこと**
> - セクション固有の楽器指示や展開（「サビで転調してストリングスが入る」など）を Style 欄に混ぜない → 歌詞側の `[ ]` メタタグへ分離する。
> - 意味が競合するタグを並べない（例：`Acoustic Ballad` と `Heavy EDM Drop` の混在）。
> - 1サビに `[Light Rhythm]` 等の弱めるタグを置かない（Bメロとの音圧逆転を防ぐため、引き算はBメロ側で行い、1サビは `[Full Band]` で解放する）。

### 3. Exclude Styles と数値パラメータの決定
- **Exclude Styles（2〜4個）**：
  - 意図しない方向へ引っ張られるのを防ぐ語を選ぶ。
  - **重要**：歌詞が暗いのに曲調を明るくしたい「対比ソング」では、歌詞のネガティブさに引きずられないよう `sad, dark, melancholy, minor key, slow ballad` を必ず含める。
- **Style Influence**：
  - 通常：`65〜75%`
  - 対比ソング（歌詞と曲調が逆）：`80%`（曲調の強制力を上げる）
- **Weirdness**：
  - 170 BPM 超のアップテンポ・複雑な譜割り：`25〜35%`（拍よれ・音飛び防止）
  - ゆったり・実験的：`40〜55%`

### 4. `styles.txt` の出力
対象フォルダ（指定があれば `~/Music\Suno\<曲名>\styles.txt`）に以下の形式で出力する（単独呼び出しで保存先指定がなければチャット上に提示する）。

```text
[Style of Music]
<先頭20〜30語にコアを凝縮した英語プロンプト>

[Exclude Styles]
<除外タグ 2〜5個>

[Parameters]
- Style Influence: <数値>%
- Weirdness: <数値>%
- Mode: Custom Mode ON / Instrumental OFF

[Design Rationale]
- 語順・楽器選定の意図：
- 歌詞とのバランス・対比設計：
```
