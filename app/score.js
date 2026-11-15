// Saf skor fonksiyonu (DOM yok): sigmoid(w·x + b). model.json Python'dan dışa aktarılır.
export function score(m, x) {
  let z = m.intercept;
  const cat = m.categorical;
  if (!(x[cat.column] in cat.coef)) throw new Error("bilinmeyen " + cat.column + ": " + x[cat.column]);
  z += cat.coef[x[cat.column]];
  for (const [c, n] of Object.entries(m.numeric)) z += n.coef * ((x[c] - n.mean) / n.scale);
  for (const [c, w] of Object.entries(m.binary)) z += w * (x[c] ? 1 : 0);
  return 1 / (1 + Math.exp(-z));
}
export const isUrgent = (m, p) => p >= m.threshold;
