# ⑥ 編曲家：Style of Music 設計

## Style of Music（パターン C：短い自然言語・2文）
Japanese indie ballad at 76 BPM with an intimate soft female vocal and suspended chords. Soft felt piano leads the quiet verses and outro, while warm synth pads and brushed percussion gently open up the choruses with gradual warmth.

## 設計意図
- **ジャンル・BPM・声質**：日本語の静かな語りを損なわない `Japanese indie ballad at 76 BPM` と `intimate soft female vocal`、`suspended chords` を第1文に配置（音圧が落ちる `Fragile` や過剰な盛り上げ語は不使用）。
- **静/動の楽器役割分担**：第2文で静かなパート（`Soft felt piano leads the quiet verses and outro`）とサビでの広がり（`warm synth pads and brushed percussion gently open up the choruses with gradual warmth`）を分け、歌詞側の `[Solo Piano]` / `[Stripped Back]` / `[Sparse Piano]` がバンド楽器に押し切られずに効くよう設計。
- **メタタグ最小化**：`Only` 系（`[Piano Only]`）と `[Add 〜]` 連打を廃止し、構造タグ＋転換点3か所（`[Solo Piano]`, `[Stripped Back]`, `[Sparse Piano]`）＋終止 `[End]` に整理。
- **利用プラン**：無料版（Free）のため Exclude Styles / パラメータ出力は省略。