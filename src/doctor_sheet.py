"""docs/DOKTOR_INCELEME.md üretir: synth.py varsayımlarının doktor inceleme föyü (sayılar koddan okunur)."""
import datetime
import pathlib

import synth as S

COND = {"cardiac": "Kardiyak acil", "panic": "Panik/anksiyete", "reflux": "Reflü", "msk": "Kas-iskelet"}
PAINTR = {"pressure": "Baskı/sıkışma", "sharp": "Keskin/batıcı", "burning": "Yanma", "ache": "Künt/sızı", "other": "Diğer"}
GROUPS = [
    ("Ağrı özellikleri", {
        "radiates_arm_jaw": "Kola/çeneye yayılma", "exertional_onset": "Eforla başlama",
        "onset_during_stress": "Stres/heyecanla başlama", "worse_breath_or_movement": "Nefes/harekette artma",
        "tender_on_pressing": "Bastırınca ağrıma"}),
    ("Eşlik eden belirtiler", {
        "sweating_cold": "Soğuk terleme", "nausea": "Bulantı/kusma", "short_breath": "Nefes darlığı",
        "tingling_hands_lips": "El/dudak karıncalanması", "fear_of_dying": "Ölüm korkusu",
        "palpitations": "Çarpıntı"}),
    ("Rahatlatan/kötüleştiren etkenler", {
        "worse_after_meal_or_lying": "Yemek sonrası/yatınca artma", "relieved_by_antacid": "Antasitle azalma",
        "relieved_by_rest": "Dinlenmeyle azalma"}),
    ("Öykü ve risk faktörleri", {
        "prior_panic_history": "Geçmiş panik atak", "smoker": "Sigara", "hypertension": "Hipertansiyon",
        "diabetes": "Diyabet", "family_heart_history": "Erken yaşta aile kalp öyküsü",
        "high_cholesterol": "Yüksek kolesterol"}),
]
LABELS = {k: v for _, g in GROUPS for k, v in g.items()}
assert set(LABELS) == set(S.BIN), set(LABELS) ^ set(S.BIN)

p = lambda x: f"{x * 100:g}"
head = lambda *c: "| " + " | ".join(c) + " |\n|" + "---|" * len(c) + "\n"
names = [COND[c] for c in S.CLASSES]
atyp_mult = .4  # synth.py'de literal (.4); CLASSIC listesi koddan okunur
base, fem, dia = .15, .20, .20  # synth.py'de literal p_atyp katsayıları; sürüklenirse aşağıdaki assert yakalar
_src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
assert ".15 + .20 * (1 - rows.male) + .20 * rows.diabetes" in _src and "pr * .4" in _src, "synth atipik kuralı değişti"
exp_atyp = base + fem * (1 - S.MALE["cardiac"]) + dia * S.BIN["diabetes"][0]  # kardiyakte beklenen atipik oranı

o = ["# Göğüs ağrısı triyaj prototipi: klinik varsayım inceleme föyü\n",
     "**Amaç:** Aşağıdaki sayılar, bir prototip için SENTETİK eğitim vakaları üretirken kullandığımız VARSAYIMLARDIR; ölçülmüş değildir.  ",
     "Lütfen yanlış bulduğunuz sayıyı \"Düzeltme\" sütununa yazın veya makul ise \"makul\" yazın.  ",
     "Sonuçlar gerçek hastalarda doğrulanmamıştır; bu föy bir tanı/tedavi aracı için değildir.\n",
     "## 1. Durum dağılımı\n", head("Durum", "Önsel %", "Yaş ort±sd", "Erkek %", "Süre medyanı (dk)", "Düzeltme")]
for c, pr in zip(S.CLASSES, S.PRIORS):
    a = S.AGE[c]
    o.append(f"| {COND[c]} | {p(pr)} | {a[0]}±{a[1]} | {p(S.MALE[c])} | {S.DUR_MEDIAN_SD[c][0]} | |\n")
o += ["\n## 2. Ağrı tipi dağılımı (%)\n", head("Ağrı tipi", *names, "Düzeltme")]
for i, t in enumerate(S.PAIN_TYPES):
    o.append(f"| {PAINTR[t]} | " + " | ".join(p(S.PAIN[c][i]) for c in S.CLASSES) + " | |\n")
for c in S.CLASSES:
    assert abs(sum(S.PAIN[c]) * 100 - 100) <= 1, c
o += ["\n## 3. Belirti ve risk faktörü olasılıkları (%)\n",
      "Her hücre: o durumdaki hastaların bu özelliğe \"evet\" deme olasılığı.\n\n", head("Özellik", *names, "Düzeltme")]
for gname, g in GROUPS:
    o.append(f"| **{gname}** | | | | | |\n")
    for k, lab in g.items():
        o.append(f"| {lab} | " + " | ".join(p(v) for v in S.BIN[k]) + " | |\n")
cl = ", ".join(LABELS[k].lower() for k in S.CLASSIC)
o += ["\n## 4. Atipik sunum kuralı\n",
      f"Kardiyak hastaların atipik sunum olasılığı: taban %{p(base)}, kadınsa +%{p(fem)}, diyabet varsa +%{p(dia)} "
      f"(kadın + diyabet: %{p(base + fem + dia)}). Atipik kardiyakte klasik belirtiler ({cl}) olasılığı "
      f"{atyp_mult:g} ile çarpılır (%{p(1 - atyp_mult)} azalır) ve ağrı tipi panik dağılımından çekilir.  ",
      "Düzeltme: ........................................................\n",
      "\n## 5. Gürültü\n",
      f"Her özellik, rastgele %{p(S.NOISE)} olasılıkla tersine çevrilir (yanlış beyan/kayıt hatası simülasyonu). Düzeltme: ..........\n",
      "\n## 6. Doktora sorular\n",
      f"1. Kendi kendine triyaj uygulaması popülasyonunda %{p(S.PRIORS[0])} kardiyak önsel makul mü (muhtemelen çok daha düşük)? Sizce kaç olmalı?\n",
      "2. Hangi belirtiler ayırt etmede daha ağır basmalı, hangileri fazla önemseniyor?\n",
      f"3. Kardiyak vakaların yaklaşık %{p(exp_atyp)} kadarının atipik olması gerçekçi mi? Kadın/diyabetlide artış yeterli mi?\n",
      "4. Kırmızı bayrak listemizde eksik olan ne var? (Şu an: >15 dk ezici ağrı, yayılma, soğuk terleme/senkop, ağır nefes darlığı.)\n",
      "5. Güven verici saydığımız ama saymamamız gereken bir bulgu var mı (ör. bastırınca ağrıma, antasitle azalma)?\n",
      "6. Kaçırdığımız yaş/cinsiyet etkileşimleri var mı (ör. genç kadında, yaşlıda, böbrek/aort/PE gibi diğer acil nedenler)?\n\n",
      "Notlarınız:\n\n\n",
      f"---\nÜretim tarihi: {datetime.date.today().isoformat()} · kaynak: src/synth.py\n",
      "\nİsim/İmza: ................................  Tarih: ............\n"]
out = "".join(o)
for lab in LABELS.values():
    assert lab in out, lab
path = pathlib.Path(__file__).resolve().parent.parent / "docs" / "DOKTOR_INCELEME.md"
path.parent.mkdir(exist_ok=True)
path.write_text(out, encoding="utf-8")
print("yazıldı:", path)
