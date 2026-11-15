# kalpnet.ai: Proje Raporu (Faz 0-4)

**Canlı uygulama:** https://muzaffer0000.github.io/kalpnet.ai/app/

| Faz | Durum |
|---|---|
| 0. Hazırlık | Bitti |
| 1. Veri | Kısmen: Cleveland ve sentetik var, MIMIC-IV başvurusu yapılmadı |
| 2. Model | Bitti |
| 3. Kendini geliştirme döngüsü | Bitti |
| 4. Mobil uygulama (PWA) | Bitti, yayında |
| 5. Güvenlik ve hukuk | Başlanmadı |

## 1. Amaç ve neden

Göğüs ağrısıyla acile gelenlerin çoğunda kalp kaynaklı bir sorun çıkmıyor. Bir acil servis çalışmasında başvuruların %58,7'si anksiyete, panik veya nedeni bilinmeyen ağrı olarak sonuçlanmış; kalp dışı göğüs ağrısı olanlarda panik bozukluğu oranı %16-47 arasında. Hedef: bir kullanıcının semptomlarına bakıp ağrının acil kalp kaynaklı olma olasılığını tahmin eden, açıklanabilir bir model ve sonunda bunu kullanan bir mobil uygulama.

**Sınır:** Kalp krizi tanısı EKG ve troponin testiyle konur. Bu proje tanı koymaz; riskli durumda acile yönlendirir ve hiçbir koşulda "güvendesin" demez. Tanı koyan yazılım tıbbi cihaz sayılır (TİTCK, CE/FDA).

## 2. Ne yaptık, nasıl, neden

| Adım | Ne | Neden |
|---|---|---|
| Araştırma | Veri setleri (MIMIC-IV, UCI), HEART/EDACS skorları, panik-kalp krizi farkları | Elimizde ne var, ne eksik görmek |
| İskelet | Python ortamı, klasörler, GitHub, `.gitignore` | Veri ve modeller git'e girmesin (hasta verisi güvenliği) |
| Cleveland modeli | UCI verisinde kalp hastalığı var/yok, lojistik regresyon ve XGBoost | Gerçek veriyle gerçekçi bir kıyas çizgisi |
| Sentetik veri | 5000 vaka: kardiyak, panik, reflü, kas-iskelet | Gerçek veride panik/reflü örneği yok |
| Semptom modeli | Sentetik veride "acil kardiyak mı?" modeli | Uygulamanın gerçek girdisi semptom soruları olacak |
| Hata düzeltme | Süre dağılımlarının düzeltilmesi | Model "uzun ağrı = güvenli" diye tehlikeli bir kural öğrenmişti |

## 3. Yöntem

**Cleveland (gerçek veri, 303 hasta).** `num` sütunu 0 = sağlıklı, 1-4 = hastalık var olarak ikiye indirildi. 6 eksik değer medyanla dolduruldu. 5 katlı çapraz doğrulamayla her hasta eğitimde görülmeden test edildi.

**Sentetik veri.** Her vakaya önce bir durum atanır (kardiyak %15, panik %35, reflü %25, kas-iskelet %25), sonra yaş, cinsiyet, ağrı tipi, süre ve 20 evet/hayır belirtisi durum bazlı olasılıklarla üretilir. Gerçekçilik için: kardiyak vakaların yaklaşık %30'u atipik (klasik belirtileri zayıf; kadın ve diyabetlide daha sık) ve her belirtiye %5 gürültü eklendi.

**Semptom modeli.** Lojistik regresyon (açıklanabilir, telefona kolay çevrilir), kalp krizi vakalarına ağırlıklı. %70 eğitim / %30 test. Alarm eşiği **yalnızca eğitim verisinden**, gerçek kalp krizlerinin %98'ini yakalayacak şekilde seçildi; test setine bakılmadı.

## 4. Sonuçlar

**Cleveland (gerçek veri), 5 katlı çapraz doğrulama:**

| Model | AUC | Eşik | Duyarlılık | Özgüllük | Kaçırılan hasta (303) |
|---|---|---|---|---|---|
| Lojistik | 0,90 | 0,50 | %77 | %87 | 32 |
| Lojistik | 0,90 | 0,14 | %95 | %53 | 7 |
| XGBoost | 0,90 | 0,50 | %73 | %84 | 37 |
| XGBoost | 0,90 | 0,13 | %95 | %60 | 7 |

**Semptom modeli (sentetik veri, 1500 test vakası, düzeltilmiş süreler):**

| Grup | Duyarlılık | Özgüllük | Kaçırılan |
|---|---|---|---|
| Tümü | %99,1 | %83,7 | 2 |
| Kadın | %99,0 | %86,7 | 1 |
| Diyabetli | %100 | %73,6 | 0 |
| 65 yaş üstü | %100 | %24,3 | 0 |

## 5. Sınırlamalar (dürüst değerlendirme)

1. **Sentetik sonuçlar sahte iyi.** AUC 0,99 ve %99 duyarlılık, olasılıkları bizim yazdığımız kuralların geri öğrenilmesinden geliyor. Gerçek dünyada doğru çalıştığını kanıtlamaz. Gerçek veriyle (MIMIC-IV) doğrulama şart.
2. **Olasılıklar varsayım.** Hepsi klinik genel bilgiye dayanan tahmin; bir kardiyolog veya acil doktoru tarafından doğrulanmadı. Atipik oranı (%30) literatürden teyit edilmedi.
3. **Gerçek veride hedefe ulaşılamadı.** Cleveland'da en iyi %95 duyarlılık, o da %53-60 özgüllükle. Hedef olan %98 yok.
4. **Cleveland farklı bir soruyu yanıtlıyor.** Kalp tetkikine gelmiş hastalar; panik/reflü örneği yok, hedef "kalp hastalığı var mı".
5. **Yaşlılarda aşırı alarm.** 65 üstü özgüllük %24: kullanıcıların çoğu "acil" görür. Ürün kararı olarak doktorla tartışılmalı.
6. **Eşik seçimi** Cleveland'da hastaların tahminlerine bakılarak yapıldı, sonuç biraz iyimser.

## 6. Süreçte yakalanan hata

İlk sentetik veride kas ağrısına 4 saat medyan süre verilmişti. Model bunu öğrenip ağrı uzadıkça kalp krizi ihtimalini düşürdü. Gerçekte uzun ağrı kalp krizini dışlamaz. Süre dağılımları çakışacak biçimde genişletildi (kardiyak 22-93 dk çeyrekler, kas 37-188, reflü 30-108, panik 8-26) ve model yeniden eğitildi; bu kural kayboldu. Sentetik veriyle çalışmanın riskinin somut bir örneği.

## 7. Faz 3: Kendini geliştirme döngüsü

**Ne:** Yeni vakalar gelince model kendini yeniden eğitir, eskisiyle karşılaştırır ve sadece daha iyiyse devreye girer.

**Nasıl** (`src/retrain.py`, ortak kod `src/model_lib.py`):
1. Yeni vaka dosyası doğrulanır (sütunlar, 0/1 değerler, yaş 18-90, süre ≥ 1). Tek bir hatalı satır bile tüm dosyayı reddettirir.
2. Eğitim havuzu + yeni vakalarla aday model eğitilir.
3. Eski ve aday model, **hiç eğitimde kullanılmayan dondurulmuş test setinde** (`data/test_frozen.csv`, 1500 vaka) karşılaştırılır.
4. **Terfi kuralı:** aday daha fazla kalp krizi kaçırmıyorsa, %98 duyarlılığı koruyorsa ve ya daha az kaçırıyor ya da daha az yanlış alarm veriyorsa devreye girer. Aksi hâlde reddedilir.
5. Eski model sürüm numarasıyla saklanır, her deneme `models/registry.json` kayıt defterine yazılır.

**Neden böyle:** Telefonda canlı, kontrolsüz öğrenme tıpta tehlikelidir; tek bir kötü veri modeli bozabilir. Her güncelleme bir kapıdan geçer.

**Demo sonucu:**

| Model | Duyarlılık | Özgüllük | Kaçırılan (1500) |
|---|---|---|---|
| v1 (aktif) | %99,1 | %83,7 | 2 |
| v2 (+1000 yeni vaka) | %97,9 | %84,8 | 5 |

v2 daha az yanlış alarm veriyordu ama 3 kalp krizini daha kaçırdığı için **reddedildi**; v1 aktif kaldı. Döngü kötü bir güncellemeyi engelledi.

**Güvenlik önlemi:** `train_symptoms.py` kayıt defteri varken çalışmayı reddeder (`--reset` gerekir), model geçmişi yanlışlıkla silinmez.

**Testler:** `tests/test_retrain.py`, 7 test (hatalı dosya reddi, terfi kuralının tüm durumları, uçtan uca çalışma). Hepsi geçiyor.

## 8. Faz 4: Mobil uygulama

**Ne:** Telefonda tarayıcıdan açılan, ana ekrana eklenebilen ve internetsiz çalışan bir uygulama (PWA). Adres: https://muzaffer0000.github.io/kalpnet.ai/app/

**Nasıl:**
- Model lojistik regresyon, yani basit bir formül. `src/export_model.py` katsayıları `app/model.json`'a aktarır; telefon skoru birkaç satır JavaScript'le (`app/score.js`) hesaplar. TFLite/ONNX'e gerek kalmadı.
- **Parite testi** (`tests/test_app_parity.mjs`): telefondaki hesap, Python modeliyle 200 vakada karşılaştırıldı. En büyük fark 2×10⁻¹⁶, alarm kararlarının hepsi aynı.
- Arayüz Türkçe, telefona uygun. Hiçbir veri cihazdan çıkmaz, analitik yok.

**Güvenlik kuralları:**
- Formdan **önce** acil belirtiler listesi ve 112 butonu.
- Yüksek skor: "Acil kalp kaynaklı olabilir, hemen 112'yi arayın."
- Düşük skor: "Risk daha düşük görünüyor ama bu araç kalp krizini dışlayamaz" ve panik için nefes egzersizi. Hiçbir koşulda "güvendesiniz" demez.
- Tüm sorular **zorunlu**. İlk sürümde cevapsız sorular "Hayır" sayılıyordu; bu, örneğin "kola yayılıyor mu" atlanınca riski düşük gösterirdi. İncelemede yakalanıp düzeltildi. Ağrı türü de otomatik seçili gelmiyor.
- Ekranın altında sürekli uyarı: tıbbi cihaz değildir, tanı koymaz, sentetik veriyle eğitilmiş prototiptir.

**Telefonda deneme (tarayıcının telefon görünümünde, yayındaki sürüm):**

| Vaka | Sonuç |
|---|---|
| Klasik kalp krizi (62, erkek, baskı, kola yayılma, soğuk ter) | Acil, 112 |
| Panik (28, kadın, stres, karıncalanma, ölüm korkusu) | Düşük risk + dışlanamaz uyarısı + nefes egzersizi |
| Atipik kalp krizi (70, diyabetli, nefes darlığı, bulantı) | Acil, 112 |
| Boş form | Gönderilmedi |

## 9. Çalışma yöntemi

Faz 3 ve 4'te mimariyi ve kontrolü bir yönetici yapay zeka ajanı (Claude Opus) yaptı; kodu iki ayrı alt ajan (Claude Sonnet) paralel yazdı. Yönetici ajan kodu inceledi, üç hatayı düzeltti (cevapsız sorular, varsayılan ağrı türü, model geçmişinin silinmesi), testleri kendisi çalıştırdı ve uygulamayı tarayıcıda denedi.

## 10. Sıradaki adımlar

1. Olasılık tablosunu (`src/synth.py`, `BIN`) bir doktora gösterip düzelttirmek.
2. MIMIC-IV erişim başvurusu (günler sürebilir) ve gerçek veriyle doğrulama.
3. Yeniden eğitimde tekrar eden vakaları ayıklamak; dondurulmuş test setini periyodik yenilemek (çok sayıda denemede modelin o test setine uyum sağlamaması için).
4. Gerçek telefonlarda deneme ve kullanılabilirlik testi; yaşlılarda aşırı alarm (%24 özgüllük) sorununu doktorla değerlendirmek.
5. Hukuk: KVKK, tıbbi cihaz mevzuatı. Gelir yönü: tanısız triyaj/panik desteği, ardından klinik B2B.

## 11. Yeniden üretme

```
python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
python src/train.py                  # Cleveland modeli (data/uci_heart gerekir)
python src/synth.py                  # sentetik veri
python src/train_symptoms.py         # semptom modeli, donmuş test seti, kayıt defteri (tekrar için --reset)
python src/synth.py --seed 1 --n 1000 --out data/new_cases_demo.csv
python src/retrain.py data/new_cases_demo.csv   # kendini geliştirme demosu
python src/export_model.py           # modeli app/model.json'a aktar
python -m pytest                     # Python testleri
node tests/test_app_parity.mjs       # telefon-Python parite testi
```
