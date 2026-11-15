import { score, isUrgent } from "./score.js";

const $ = id => document.getElementById(id);
const PAIN = { pressure: "Baskı / sıkışma / ezilme", sharp: "Keskin / batıcı", burning: "Yanma", ache: "Künt / sızı", other: "Diğer / emin değilim" };
// Model girdisi (binary) -> Türkçe soru. Her model girdisi burada olmalı (build() kontrol eder).
const Q = {
  male: "Cinsiyetiniz erkek mi?",
  diabetes: "Şeker hastalığınız (diyabet) var mı?",
  radiates_arm_jaw: "Ağrı kola, çeneye veya omuza yayılıyor mu?",
  exertional_onset: "Ağrı efor (yürüme, merdiven, koşma) sırasında başladı mı?",
  onset_during_stress: "Ağrı yoğun stres veya heyecan sırasında başladı mı?",
  sweating_cold: "Soğuk terleme oldu mu?",
  nausea: "Bulantı veya kusma var mı?",
  short_breath: "Nefes darlığı var mı?",
  tingling_hands_lips: "Ellerde veya dudak çevresinde karıncalanma/uyuşma var mı?",
  fear_of_dying: "Ölüm korkusu veya 'kötü bir şey olacak' hissi var mı?",
  palpitations: "Çarpıntı (kalbin hızlı/düzensiz atması) var mı?",
  worse_breath_or_movement: "Ağrı derin nefes alınca veya hareket edince artıyor mu?",
  tender_on_pressing: "Göğsünüze bastırınca ağrı yerinde acıyor mu?",
  worse_after_meal_or_lying: "Yemekten sonra veya uzanınca ağrı artıyor mu?",
  relieved_by_antacid: "Antasit (mide ilacı) ağrıyı azalttı mı?",
  relieved_by_rest: "Dinlenince ağrı azalıyor mu?",
  prior_panic_history: "Daha önce panik atak yaşadınız mı?",
  smoker: "Sigara kullanıyor musunuz?",
  hypertension: "Yüksek tansiyonunuz var mı?",
  family_heart_history: "Ailenizde erken yaşta kalp hastalığı/kalp krizi öyküsü var mı?",
  high_cholesterol: "Kolesterolünüz yüksek mi?",
};

let model;

function yn(name, text) {
  return `<fieldset class="q"><legend>${text}</legend><div class="yn">
    <label><input type="radio" name="${name}" value="1" required><span>Evet</span></label>
    <label><input type="radio" name="${name}" value="0"><span>Hayır</span></label></div></fieldset>`;
}

function build() {
  const cat = model.categorical;
  const missing = Object.keys(model.binary).filter(k => !(k in Q));
  if (missing.length) throw new Error("Soru metni eksik: " + missing.join(", "));
  const opts = cat.categories.map(c => `<option value="${c}">${PAIN[c] || c}</option>`).join("");
  $("fields").innerHTML =
    `<label for="age">Yaşınız</label><input id="age" type="number" inputmode="numeric" min="18" max="110" required>
     <label for="pain">Ağrının türü</label><select id="pain" required><option value="" selected disabled>Seçin</option>${opts}</select>
     <label for="dur">Ağrı kaç dakikadır sürüyor?</label><input id="dur" type="number" inputmode="numeric" min="1" max="10080" required>
     <p class="small">Saat ise dakikaya çevirin (1 saat = 60). Tüm soruları cevaplayın.</p>` +
    Object.keys(model.binary).map(k => yn(k, Q[k])).join("");
}

function readInput() {
  const age = Number($("age").value), dur = Number($("dur").value);
  if (!(age >= 18 && age <= 110)) return "Lütfen yaşınızı girin (18-110).";
  if (!(dur >= 1)) return "Lütfen ağrının süresini dakika olarak girin.";
  if (!$("pain").value) return "Lütfen ağrının türünü seçin.";
  const x = { age, duration_min: dur, [model.categorical.column]: $("pain").value };
  for (const k of Object.keys(model.binary)) {
    const v = $("form").elements[k].value;  // "" = cevapsız; sessizce "Hayır" saymak riski düşük gösterir
    if (v === "") return "Lütfen tüm soruları cevaplayın: " + Q[k];
    x[k] = Number(v);
  }
  return x;
}

function show(p) {
  const urgent = isUrgent(model, p), r = $("result");
  r.hidden = false;
  r.className = "card" + (urgent ? " alert" : "");
  r.innerHTML = urgent
    ? `<h2>Acil kalp kaynaklı olabilir — hemen 112'yi arayın / acile gidin</h2>
       <p>Bu araç, verdiğiniz bilgilere göre kalp kaynaklı acil bir durumu dışlayamıyor. Beklemeyin.</p>
       <a class="btn red" href="tel:112">112'yi ara</a>`
    : `<h2>Bu araca göre risk daha düşük görünüyor</h2>
       <p>Ancak bu araç kalp krizini <strong>dışlayamaz</strong>. Şüpheniz varsa, belirtileriniz sürüyorsa ya da kötüleşiyorsa
       vakit kaybetmeden acile gidin veya 112'yi arayın.</p>
       <a class="btn red" href="tel:112">112'yi ara</a>`;
  $("breath").hidden = urgent;
  r.focus(); r.scrollIntoView({ behavior: "smooth" });
}

let timer = null;
function breathe() {
  const c = $("circle"), ph = $("phase"), b = $("breath-btn");
  if (timer) { clearTimeout(timer); timer = null; c.style.transform = ""; c.textContent = "Hazır"; ph.textContent = ""; b.textContent = "Başlat"; return; }
  b.textContent = "Durdur";
  const steps = [["Nefes alın", 4, 1.4], ["Tutun", 4, 1.4], ["Yavaşça verin", 6, 1]];
  let i = 0;
  const next = () => {
    const [t, s, sc] = steps[i++ % 3];
    c.style.transitionDuration = s + "s"; c.style.transform = `scale(${sc})`; c.textContent = ph.textContent = t;
    timer = setTimeout(next, s * 1000);
  };
  next();
}

async function init() {
  try {
    model = await (await fetch("model.json")).json();
    build();
  } catch (e) {
    $("fields").textContent = "Model yüklenemedi. Acil belirtiniz varsa 112'yi arayın.";
    console.error(e); return;
  }
  $("form").addEventListener("submit", e => {
    e.preventDefault();
    const x = readInput(), err = $("error");
    err.hidden = typeof x === "object";
    if (!err.hidden) { err.textContent = x; return; }
    show(score(model, x));
  });
  $("breath-btn").addEventListener("click", breathe);
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
}
init();
