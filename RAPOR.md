# kalpnet.ai: Proje Raporu (Faz 0-2)

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

## 7. Sıradaki adımlar

1. Olasılık tablosunu bir doktora gösterip düzelttirmek.
2. MIMIC-IV erişim başvurusu (günler sürebilir) ve gerçek veriyle doğrulama.
3. Kendini geliştirme döngüsü: yeni veri gelince otomatik yeniden eğit → eskiyle karşılaştır → daha iyiyse güncelle.
4. Modeli TFLite/ONNX'e çevirip soru formlu mobil prototip.
5. Hukuk: KVKK, tıbbi cihaz mevzuatı. Gelir yönü: tanısız triyaj/panik desteği, ardından klinik B2B.

## 8. Yeniden üretme

```
python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
python src/train.py          # Cleveland modeli (data/uci_heart gerekir)
python src/synth.py          # sentetik veri
python src/train_symptoms.py # semptom modeli
```
