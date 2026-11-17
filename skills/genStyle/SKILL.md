---
name: genStyle
description: 物語・コンセプト・ビジュアルイメージ・コア楽器から、Suno AI 用の Style of Music / Exclude Styles / 各種パラメータ（styles.txt）を生成・最適化する。「スタイルを作って」「SunoのStyleを考えて」「/genStyle」と頼まれたとき、または toSong スキルから呼び出されたときに使う。
---

# Suno Style 生成（genStyle）

曲のコンセプト・感情トーン・ビジュアルの空気感から、Suno AI が解釈できる `styles.txt` を設計する。共通仕様は `../toSong/references/Suno作曲メソッド.md`（存在する場合）を優先して従う。

## 手順

### 1. 入力情報の整理
物語・テキスト・画像から以下を確認する（不足分は妥当に補う）：
- **曲調の軸**：ストレートに寄り添うか、重い歌詞 × 明るい曲調（ギャップ対比）か
- **雰囲気・色**：情景の質感（冬の透明感、夜のネオンなど）
- **ボーカル**：性別・声質・歌い方
- **コア楽器（3〜4点）**：全編の軸になる楽器

### 2. Style of Music の組み立て（先頭 20〜25 語に集中）
Suno は先頭に強い重みを置き、矛盾タグや過剰タグ（6個以上）で平均化しやすい。必ず次の順で英語キーワードを並べる：

1. **ジャンル / サブジャンル**（例：`Hyper-cheerful J-Pop`）
2. **声質 / 歌唱スタイル**（例：`Bright Clear Female Vocal` ※ `Fragile` 等の音圧を落とす語は避ける）
3. **BPM / 拍子 / Key**（例：`175 BPM, Bright Major Key`）
4. **コア楽器（3〜4点）**（例：`Sparkling Piano, Celesta, Sleigh Bells, Tight Drums` ※ `Lush Voicings` 等の中低域を濁らせる語は避ける）
5. **全体の質感**（例：`Dynamic Contrast, Crisp Modern Production` ※ 静と動の落差には `Dynamic Contrast` を入れ、全編疾走させたい曲以外は `Driving` を外す）

※ セクション固有の展開指示は Style 欄に入れず、歌詞側の `[ ]` メタタグへ分離する。

### 3. Exclude Styles とパラメータの決定
- **Exclude Styles（2〜3個）**：意図しない方向を防ぐ語を選ぶ。対比ソングでは歌詞の暗さに引っ張られないよう `sad, dark, melancholy, minor key, slow ballad` 等を入れる。
- **Style Influence**：通常 `65〜75%`／対比ソング `80%`
- **Weirdness**：`30%` 前後（170 BPM 超の高速曲は `25〜35%`）

### 4. `styles.txt` の出力
対象フォルダ（指定があれば `work/styles.txt` 等、単独実行時はチャット提示）に以下を出力する（無料プラン時は貼り付け用として `style.txt` のみ使い、Exclude / Parameters は参考記録とする）。

```text
[Style of Music]
<先頭20〜25語にコアを凝縮した英語プロンプト>

[Exclude Styles]
<除外タグ 2〜3個>

[Parameters]
- Style Influence: <数値>%
- Weirdness: <数値>%
- Mode: Custom Mode ON / Instrumental OFF

[Design Rationale]
- 語順・楽器選定の意図：
- 歌詞とのバランス・対比設計：
```
