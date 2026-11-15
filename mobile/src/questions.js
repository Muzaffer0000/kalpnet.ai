// app/app.js'ten birebir kopya (aynı anahtarlar, aynı sıra).
export const PAIN = { pressure: "Baskı / sıkışma / ezilme", sharp: "Keskin / batıcı", burning: "Yanma", ache: "Künt / sızı", other: "Diğer / emin değilim" };
// Model girdisi (binary) -> Türkçe soru. Her model girdisi burada olmalı (build() kontrol eder).
export const Q = {
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
