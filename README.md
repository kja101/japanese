# 日本語 — Japanese study tools

Free, open, browser-based tools for learning Japanese, from kana to the JLPT N2 kanji.
Every tool is a single self-contained HTML file: no build step, no server, no account.
Open `index.html` locally or visit the site: <https://kja101.github.io/japanese/>

## The tools

| Page | What it is |
|---|---|
| `kanji/master-kanji-shapes.html` | **Look up and explore.** Every kanji from N5 to N2 (1,086), with a cumulative level switch. Each card: parts and story, look-alikes, and every word grouped by on and kun reading, linked to the other kanji in it. Four views: Course (shape families), Flashcards, Sound index (parts that give the sound, shared readings) and By topic. Your own stories. |
| `kanji/learn.html` | **Learn day by day.** Daily study plan: how to learn kanji fastest, plus spaced-repetition flashcards from N5 up to N2, with optional word cards from the 4,205-word list. Shares progress and your own stories with the master deck. |
| `kanji/kanji-by-situation.html` | **See them in use.** 200 N4 kanji in 13 real-life situations, with 1,465 example sentences, where you meet each kanji, and N5–N2 word lists. |
| `words/phrasebook.html` | Interactive phrasebook: 285 phrases and 1,465 sentences in 14 situations, with swap-in words, grammar-block colouring and a starred personal list. |
| `words/vocabulary.html` | **Every word.** 4,205 N5–N2 words (the kanji words plus the kana lists) by type or kana order, with examples, audio and links to the kanji deck. |
| `words/grammar.html` | 112 grammar patterns from N5 to N2, with a cumulative level switch: meaning, how to form each, usage notes, and examples with audio. |
| `words/sentence-builder.html` | **The grammar behind it.** 1,465 sentences in 13 situations, in colour-coded blocks with a level switch, the English order beside the Japanese, and all N5/N4 verbs and adjectives with their forms. |
| `words/phrase-guide.html` | Earlier phrase guide, now included in the phrasebook. Kept so old links still work; not part of the build. |
| `kana/kana-words.html` | 454 N5–N2 words written in kana, grouped by use (greetings, question and pointing words, linking words, adverbs, sound words, verbs, nouns by topic), with example sentences. |
| `kana/katakana-words.html` | 353 N5–N2 loanwords by topic, with notes on false friends and non-English origins, and example sentences. |
| `kana/kana-sounds.html` | Kana by sign family, by sound, and same-sound words with pitch patterns. |

Sentences on the phrasebook, sentence builder, grammar, situation, word and kana pages are coloured by grammar block (who, time, place, how, what, verb, question), with one on/off setting shared by every page. Every page can read the Japanese aloud with the browser's built-in Japanese voice (the ▶ buttons). All pages share one colour code for readings: **indigo** for on readings (from Chinese), **green** for kun readings (native Japanese), **red dotted** for special whole-word readings.

## Offline

Once you've opened the site, it works without a connection: add it to your phone's home screen and it runs like an app. After each push, the new version downloads in the background and is used from the next visit.

## Your data stays on your device

Progress, flashcard status and the stories you write are saved in your browser's local storage. Nothing is sent anywhere. Use the export and import buttons to back up or move between devices.

## Run locally

```sh
git clone https://github.com/kja101/japanese.git
open japanese/index.html
```

## How the site is built

The pages in `kanji/`, `words/` and `kana/` are generated. Don't edit them directly: edit the templates or the data, then rebuild.

```
src/      page templates (HTML), plus src/common.js
data/     the content, as JSON
build/    build.py, which puts the two together
assets/   common.js, shared by every page: reading engine, audio, particles, progress and stories (generated)
```

To rebuild after a change (Python 3, no packages needed):

```sh
python3 build/build.py
```

Then commit both the source change and the rebuilt pages, because GitHub Pages serves the built files.

### Where to edit what

| To change | Edit |
|---|---|
| A kanji's story, keyword, parts or look-alikes | `data/kanji.json` (under `K`, by kanji) |
| The words listed on kanji cards | `data/kanji-words.json` |
| Readings used for the on/kun colours | `data/readings.json` |
| The 120 core sentence-builder sentences | `data/sentences-builder.json` |
| Natural English for those sentences | `data/sentence-builder-english.json` |
| The other example sentences | `data/sentences-extra.json` |
| Phrasebook sections and swap-in words | `data/phrasebook.json` |
| Situation topics, kanji rows and notes | `data/situation.json` |
| Kana words and their groups | `data/kana-words.json` (hiragana), `data/katakana-words.json` (katakana); both pages share `src/kana-words.html` |
| Grammar patterns and examples | `data/grammar.json` |
| Offline caching | `src/sw.js` (the build writes `sw.js` with the file list and a version) |
| The daily study plan's order for N5/N4 (N3 and N2 are added automatically) | `data/study.json` |
| Page layout or behaviour | the matching file in `src/` |

## Sources and credits

- **N5 and N4 kanji lists** follow the community (tanos.co.uk) lists. **N3 and N2 kanji levels** follow Jonathan Waller's JLPT lists. JLPT has not published official lists since 2010, so all levels are a guide.
- **Readings and meanings** for the N3 and N2 kanji come from **KANJIDIC2**, © the Electronic Dictionary Research and Development Group (EDRDG), used under the EDRDG licence (CC BY-SA 4.0). <https://www.edrdg.org/edrdg/licence.html>
- **Shape breakdowns** for the N3 and N2 kanji are derived from the **CHISE IDS database** via [cjkvi-ids](https://github.com/cjkvi/cjkvi-ids), distributed under the GNU GPL.
- **Vocabulary levels** come from [jlpt-word-list](https://github.com/elzup/jlpt-word-list) (MIT), derived from the tanos.co.uk lists.
- The learning method draws on James Heisig's *Remembering the Kanji* approach, WaniKani/Tofugu and the Anki community. This project is not affiliated with any of them, and all stories, look-alike notes and explanations are original.

## Licence

See [LICENSE.md](LICENSE.md).
