// Saf girdi doğrulama (React Native bağımlılığı yok); app/app.js readInput ile aynı sıra ve mesajlar.
import { Q } from "./questions.js";

// raw = { age: "", dur: "", pain: "", answers: { [anahtar]: "1" | "0" } }
export function readInput(model, raw) {
  const age = Number(raw.age), dur = Number(raw.dur);
  if (!(age >= 18 && age <= 110)) return "Lütfen yaşınızı girin (18-110).";
  if (!(dur >= 1)) return "Lütfen ağrının süresini dakika olarak girin.";
  if (!raw.pain) return "Lütfen ağrının türünü seçin.";
  const x = { age, duration_min: dur, [model.categorical.column]: raw.pain };
  for (const k of Object.keys(model.binary)) {
    const v = raw.answers?.[k] ?? "";  // "" = cevapsız; sessizce "Hayır" saymak riski düşük gösterir
    if (v === "") return "Lütfen tüm soruları cevaplayın: " + Q[k];
    x[k] = Number(v);
  }
  return x;
}
