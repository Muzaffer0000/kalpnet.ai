import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { score, isUrgent } from "./score.js";
import { Q } from "./questions.js";
import { readInput } from "./validate.js";

const model = JSON.parse(readFileSync(new URL("./model.json", import.meta.url)));
const fx = JSON.parse(readFileSync(new URL("../../tests/parity_cases.json", import.meta.url)));
const keys = Object.keys(model.binary);
const toRaw = i => ({
  age: String(i.age), dur: String(i.duration_min), pain: i.pain_type,
  answers: Object.fromEntries(keys.map(k => [k, String(i[k])])),
});
const base = () => toRaw(fx.cases[0].input);
const msg = k => "Lütfen tüm soruları cevaplayın: " + Q[k];

test("her model sorusunun metni var", () => {
  assert.deepEqual(keys.filter(k => !(k in Q)), []);
});

test("cevapsız soru engellenir", () => {
  for (const k of keys) {
    const r = base(); delete r.answers[k];
    assert.equal(readInput(model, r), msg(k));
    r.answers[k] = ""; assert.equal(readInput(model, r), msg(k));
  }
  assert.equal(readInput(model, { ...base(), answers: {} }), msg(keys[0]));
});

test("ağrı türü seçilmemişse engellenir", () => {
  assert.equal(readInput(model, { ...base(), pain: "" }), "Lütfen ağrının türünü seçin.");
});

test("yaş sınırları", () => {
  const ageErr = "Lütfen yaşınızı girin (18-110).";
  for (const a of ["17", "111", "", "abc"]) assert.equal(readInput(model, { ...base(), age: a }), ageErr, a);
  for (const a of ["18", "110"]) assert.equal(typeof readInput(model, { ...base(), age: a }), "object", a);
});

test("süre sınırları", () => {
  const durErr = "Lütfen ağrının süresini dakika olarak girin.";
  for (const d of ["0", ""]) assert.equal(readInput(model, { ...base(), dur: d }), durErr, d);
  assert.equal(typeof readInput(model, { ...base(), dur: "1" }), "object");
});

test("kontrol sırası: yaş, süre, ağrı türü, sorular", () => {
  const bad = { age: "", dur: "", pain: "", answers: {} };
  assert.match(readInput(model, bad), /yaşınızı/);
  assert.match(readInput(model, { ...bad, age: "40" }), /süresini/);
  assert.match(readInput(model, { ...bad, age: "40", dur: "5" }), /türünü/);
  assert.match(readInput(model, { ...bad, age: "40", dur: "5", pain: model.categorical.categories[0] }), /tüm soruları/);
});

const urgentCase = fx.cases.find(c => c.p >= fx.threshold);
const panicCase = fx.cases.find(c => c.p < fx.threshold && (c.input.prior_panic_history || c.input.tingling_hands_lips))
  ?? fx.cases.find(c => c.p < fx.threshold);
for (const [name, c] of [["acil", urgentCase], ["düşük risk (panik benzeri)", panicCase]]) {
  test("fixture vakası: " + name, () => {
    assert.ok(c, "fixture'da vaka yok");
    assert.equal(model.threshold, fx.threshold);
    const x = readInput(model, toRaw(c.input));
    assert.deepEqual(x, c.input);
    const s = score(model, x);
    assert.ok(Math.abs(s - c.p) < 1e-9);
    assert.equal(isUrgent(model, s), c.p >= fx.threshold);
  });
}
