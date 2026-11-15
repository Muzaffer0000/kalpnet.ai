// node tests/test_mobile_parity.mjs  (önce: python tests/make_parity_fixture.py; mobile'da: npm run sync-model)
import { readFileSync, existsSync } from "node:fs";
import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";

const p = f => fileURLToPath(new URL(f, import.meta.url));
for (const [a, b] of [["../app/score.js", "../mobile/src/score.js"], ["../app/model.json", "../mobile/src/model.json"]]) {
  assert.ok(existsSync(p(b)), `${b} yok. 'cd mobile && npm run sync-model' çalıştırın.`);
  assert.ok(readFileSync(p(a)).equals(readFileSync(p(b))), `${b} ${a} ile aynı değil. 'cd mobile && npm run sync-model' çalıştırın.`);
}
const { score, isUrgent } = await import("../mobile/src/score.js");
const rd = f => JSON.parse(readFileSync(p(f)));
const model = rd("../mobile/src/model.json"), fx = rd("./parity_cases.json");
assert.equal(model.threshold, fx.threshold, "eşik uyuşmuyor (model.json ile fixture farklı sürümden)");
let maxd = 0, urgent = 0;
for (const { input, p: exp } of fx.cases) {
  const s = score(model, input);
  maxd = Math.max(maxd, Math.abs(s - exp));
  assert.ok(Math.abs(s - exp) < 1e-9, `skor farkı ${s} vs ${exp}`);
  assert.equal(isUrgent(model, s), exp >= fx.threshold, "eşik kararı farklı");
  urgent += isUrgent(model, s);
}
console.log(`OK (mobile): ${fx.cases.length} vaka, maks fark ${maxd.toExponential(2)}, ${urgent} acil, kopyalar byte-aynı`);
