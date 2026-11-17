// Render every page that shows coloured sentences and check that the Japanese line
// and the English line carry the same set of block colours. Run with the site served
// locally:  python3 -m http.server 8765  &&  node build/check_rendered.js
const { chromium } = require('playwright');

const BASE = process.env.BASE || 'http://localhost:8765';
const PAGES = [
  // tier 2 = every level, so the check sees all 1,400-odd sentences, not just N5
  { url: 'words/sentence-builder.html', row: '.sent', jp: '.lay-kanji', en: '.lay-en',
    before: () => { const b = document.querySelector('[data-tier="2"]'); if (b) b.click(); } },
  { url: 'words/phrasebook.html', row: '.it', jp: '.jpl', en: '.enl' },
  { url: 'words/grammar.html', row: '.grow', jp: '.j', en: '.t',
    before: () => { const b = document.querySelector('[data-tier="2"]'); if (b) b.click(); } },
  { url: 'words/grammar.html?view=cards', row: '.gx li', jp: '.j', en: '.t',
    before: () => {
      const b = document.querySelector('[data-tier="2"]'); if (b) b.click();
      const c = [...document.querySelectorAll('button,[data-view]')]
        .find(e => /card/i.test(e.textContent || e.dataset.view || '')); if (c) c.click();
    } },
  { url: 'words/patterns.html', row: '.ex, .mex', jp: '.j', en: '.t' },
  { url: 'kana/kana-words.html', row: '.ex', jp: '.j', en: '.t' },
  { url: 'kana/katakana-words.html', row: '.ex', jp: '.j', en: '.t' },
  { url: 'kanji/kanji-by-situation.html', row: '.sl li', jp: '.sj', en: '.se' },
];

// Walk the whole page so anything rendered lazily gets built before we look at it.
async function loadAll(page) {
  // the big pages render a section at a time; call their filler for every section directly
  await page.evaluate(() => {
    for (const [fn, list] of [['fillSection', 'SEC'], ['fillGroup', 'GROUPS']]) {
      const f = window[fn], n = window[list] && window[list].length;
      if (typeof f === 'function' && n) for (let i = 0; i < n; i++) try { f(i); } catch (e) {}
    }
  });
  await page.waitForTimeout(500);
  let last = -1;
  for (let i = 0; i < 60; i++) {
    const h = await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
      return document.body.scrollHeight;
    });
    await page.waitForTimeout(250);
    if (h === last) break;
    last = h;
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(300);
}

(async () => {
  const browser = await chromium.launch();
  let bad = 0, seen = 0, pagesWithErrors = 0;

  for (const spec of PAGES) {
    const page = await browser.newPage({ viewport: { width: 900, height: 1200 } });
    const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    await page.goto(`${BASE}/${spec.url}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(800);
    if (spec.before) { await page.evaluate(spec.before); await page.waitForTimeout(500); }
    await loadAll(page);

    const rows = await page.evaluate(({ row, jp, en }) => {
      const roles = el => {
        if (!el) return null;
        const s = new Set();
        el.querySelectorAll('.ck[data-r]').forEach(k => { if (k.dataset.r) s.add(k.dataset.r); });
        return [...s].sort();
      };
      const out = [];
      document.querySelectorAll(row).forEach(r => {
        const j = roles(r.querySelector(jp)), e = roles(r.querySelector(en));
        if (!j || !e || (!j.length && !e.length)) return;
        if (j.join() !== e.join())
          out.push({ jp: j, en: e, text: (r.innerText || '').replace(/\s+/g, ' ').slice(0, 110) });
      });
      return { bad: out, total: document.querySelectorAll(row).length };
    }, { row: spec.row, jp: spec.jp, en: spec.en });

    seen += rows.total;
    bad += rows.bad.length;
    if (errors.length) pagesWithErrors++;
    console.log(`${spec.url}: ${rows.total} rows, ${rows.bad.length} mismatched` +
      (errors.length ? `, ${errors.length} PAGE ERRORS` : ''));
    errors.slice(0, 3).forEach(e => console.log('    !', e));
    rows.bad.slice(0, 25).forEach(b =>
      console.log(`    JP ${b.jp.join('')} vs EN ${b.en.join('')}  ${b.text}`));
    await page.close();
  }

  await browser.close();
  console.log(`\n${seen} rendered rows checked, ${bad} colour mismatches, ${pagesWithErrors} pages with script errors`);
  process.exit(bad || pagesWithErrors ? 1 : 0);
})();
