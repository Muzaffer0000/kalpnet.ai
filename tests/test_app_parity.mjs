// node tests/test_app_parity.mjs  (önce: python tests/make_parity_fixture.py)
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";
import { score, isUrgent } from "../app/score.js";

const rd = f => JSON.parse(readFileSync(fileURLToPath(new URL(f, import.meta.url))));
const model = rd("../app/model.json"), fx = rd("./parity_cases.json");
assert.equal(model.threshold, fx.threshold, "eşik uyuşmuyor (model.json ile fixture farklı sürümden)");
let maxd = 0, urgent = 0;
for (const { input, p } of fx.cases) {
  const s = score(model, input);
  maxd = Math.max(maxd, Math.abs(s - p));
  assert.ok(Math.abs(s - p) < 1e-9, `skor farkı ${s} vs ${p}`);
  assert.equal(isUrgent(model, s), p >= fx.threshold, "eşik kararı farklı");
  urgent += isUrgent(model, s);
}
console.log(`OK: ${fx.cases.length} vaka, maks fark ${maxd.toExponential(2)}, ${urgent} acil`);
