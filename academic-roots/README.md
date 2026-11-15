# Academic Roots

Public URL: https://hrkoyama.github.io/academic-roots/

Japanese academic-lineage tool. Visitors create a research request for their own AI, import the returned JSON, review sources, and export text, PNG, JSON, or a fragment-only share link. No account or API key is required; no LLM/search API is called by this site.

`app.js` renders the five-person example from `data.json`. `llm-builder.js` handles local storage, import, review and export. `research-model.mjs` validates evidence and shared data without treating AI trust flags as verification. The evidence dataset and application behavior are unchanged by the hosting move.

Run `node --test scripts/research-model.test.mjs` from the repository root.

Saved user data belongs to the browser origin and does not move automatically between domains. Exported JSON can be imported at this URL. Share links created here use this site's current origin. Imported/shared creator confirmations are not treated as independent verification.

Code: MIT (`LICENSE.txt`). Text, figures, photos, external sources and visitor data have separate rights boundaries; see `rights.html`.
