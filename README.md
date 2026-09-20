# 日本語 — Japanese study tools

Free, open, browser-based tools for learning Japanese, from kana to the JLPT N2 kanji.
Every tool is a single self-contained HTML file: no build step, no server, no account.
Open `index.html` locally or visit the GitHub Pages site.

## The tools

| File | What it is |
|---|---|
| `kanji/master-kanji-shapes.html` | **Start here.** All 981 N5–N2 kanji in shape families, with a cumulative level switch (N5, N4, N3, N2). Each card: parts and story, look-alikes, and readings split into on and kun with real words. Every compound is listed on the card of each kanji in it and links between them. Chapter sound maps, a sound index, flashcards and your own stories. |
| `kanji/learn-n5-n4.html` | The learning method, plus spaced-repetition flashcards for the 284 N5/N4 kanji. |
| `kanji/kanji-by-shape-sound-topic.html` | The N5/N4 kanji by shape family, by sound (including sound-giving parts) and by topic. |
| `kanji/kanji-by-situation.html` | N4 kanji grouped by real-world situation. |
| `kanji/master-kanji-shapes-n5-n4.html` | The earlier N5/N4-only edition of the shapes deck. |
| `words/vocab-sheets.html` | Vocabulary by topic, grouped by shared kanji. |
| `words/phrase-guide.html` | Phrase frames with swap-in words. |
| `words/sentence-builder.html` | 120 sentences in colour-coded grammar blocks. |
| `kana/kana-sounds.html` | Kana by sign, by sound, and same-sound words. |

All tools share one colour code for readings: **indigo** for on readings (from Chinese), **green** for kun readings (native Japanese), **red dotted** for special whole-word readings.

## Your data stays on your device

Progress, flashcard status and the stories you write are saved in your browser's local storage. Nothing is sent anywhere. Use the export and import buttons to back up or move between devices.

## Run locally

```sh
git clone https://github.com/<your-username>/japanese.git
open japanese/index.html
```

## Sources and credits

- **N5 and N4 kanji lists** follow the community (tanos.co.uk) lists. **N3 and N2 kanji levels** follow Jonathan Waller's JLPT lists. JLPT has not published official lists since 2010, so all levels are a guide.
- **Readings and meanings** for the N3 and N2 kanji come from **KANJIDIC2**, © the Electronic Dictionary Research and Development Group (EDRDG), used under the EDRDG licence (CC BY-SA 4.0). <https://www.edrdg.org/edrdg/licence.html>
- **Shape breakdowns** for the N3 and N2 kanji are derived from the **CHISE IDS database** via [cjkvi-ids](https://github.com/cjkvi/cjkvi-ids), distributed under the GNU GPL.
- **Vocabulary levels** come from [jlpt-word-list](https://github.com/elzup/jlpt-word-list) (MIT), derived from the tanos.co.uk lists.
- The learning method draws on James Heisig's *Remembering the Kanji* approach, WaniKani/Tofugu and the Anki community. This project is not affiliated with any of them, and all stories, look-alike notes and explanations are original.

## Licence

See [LICENSE.md](LICENSE.md).
