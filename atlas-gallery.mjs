export function galleryMatches(record, group, query, runnableOnly = false) {
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase().replace(/[‐‑–—−]/g, '-');
  const words = normalize(query).trim().split(/\s+/).filter(Boolean);
  const text = normalize(record.search);
  const runnable = record.runnable === true || record.runnable === 'true';
  return (!runnableOnly || runnable) && (group === 'all' || record.group === group) && words.every(word => text.includes(word));
}

if (typeof document !== 'undefined') {
  for (const section of document.querySelectorAll('[data-gallery]')) {
    const input = section.querySelector('input[type="search"]');
    const buttons = [...section.querySelectorAll('[data-gallery-group]')];
    const tiles = [...section.querySelectorAll('[data-problem-id]')];
    const status = section.querySelector('[data-gallery-count]');
    const executionFilter = section.querySelector('[data-gallery-runnable]');
    let group = 'all';
    let runnableOnly = false;
    const update = () => {
      let count = 0;
      for (const tile of tiles) {
        tile.hidden = !galleryMatches(tile.dataset, group, input.value, runnableOnly);
        if (!tile.hidden) count++;
      }
      status.textContent = section.lang === 'ja' ? `${count} / ${tiles.length} 問題を表示` : `Showing ${count} of ${tiles.length} problems`;
      section.querySelector('[data-gallery-empty]').hidden = count !== 0;
      for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.galleryGroup === group));
      executionFilter.setAttribute('aria-pressed', String(runnableOnly));
    };
    for (const button of buttons) button.addEventListener('click', () => { group = button.dataset.galleryGroup; update(); });
    input.addEventListener('input', update);
    executionFilter.addEventListener('click', () => { runnableOnly = !runnableOnly; update(); });
    section.querySelector('[data-gallery-reset]').addEventListener('click', () => { group = 'all'; runnableOnly = false; input.value = ''; update(); input.focus(); });
    update();
  }
}
