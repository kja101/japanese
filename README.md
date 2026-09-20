# 日本語 — Japanese study tools

Free, open, browser-based tools for learning Japanese, from kana to the JLPT N2 kanji.
Every tool is a single self-contained HTML file: no build step, no server, no account.
Open `index.html` locally or visit the site: <https://kja101.github.io/japanese/>

## The tools

| Page | What it is |
|---|---|
| `kanji/master-kanji-shapes.html` | **Start here.** The main deck: all 981 N5–N2 kanji in 61 shape families, with a cumulative level switch (N5, N4, N3, N2). Each card: parts and story, look-alikes, and every word grouped by on and kun reading, with compounds listed on and linked to each kanji in them. Chapter sound maps, a sound index, flashcards, and your own stories. |
| `kanji/learn-n5-n4.html` | Daily study plan: how to learn kanji fastest, plus spaced-repetition flashcards for the 284 N5/N4 kanji in 29 lessons, parts before the kanji built from them. |
| `kanji/kanji-by-situation.html` | 200 N4 kanji in 13 real-life situations, with 222 example sentences, where you meet each kanji, and N5–N2 word lists. |
| `kanji/kanji-by-shape-sound-topic.html` | The 284 N5/N4 kanji by shape family, by sound (including sound-giving parts) and by topic, each with N5–N2 words by reading. |
| `kanji/master-kanji-shapes-n5-n4.html` | Classic edition of the shapes deck: N5/N4 kanji and words only. Superseded by the N5–N2 deck. |
| `words/phrasebook.html` | Interactive phrasebook: about 500 phrases and sentences in 14 situations, with swap-in words, grammar-block colouring and a starred personal list. |
| `words/sentence-builder.html` | The grammar lesson behind the phrasebook: 120 sentences in colour-coded blocks. |
| `words/phrase-guide.html` | Earlier phrase guide, now included in the phrasebook. Kept so old links still work. |
| `words/vocab-sheets.html` | About 390 common words across 11 topics, grouped by shared kanji. |
| `kana/kana-sounds.html` | Kana by sign family, by sound, and same-sound words with pitch patterns. |

All pages share one colour code for readings: **indigo** for on readings (from Chinese), **green** for kun readings (native Japanese), **red dotted** for special whole-word readings.

## Your data stays on your device

Progress, flashcard status and the stories you write are saved in your browser's local storage. Nothing is sent anywhere. Use the export and import buttons to back up or move between devices.

## Run locally

```sh
git clone https://github.com/kja101/japanese.git
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
