# kalpnet.ai

Göğüs ağrısı risk değerlendirme projesi: ağrının acil kalp kaynaklı olma olasılığını tahmin eden, açıklanabilir bir model ve onu kullanan mobil uygulama.

> **Uyarı:** Bu proje tıbbi cihaz değildir ve tanı koymaz. Kalp krizi tanısı EKG ve troponin testiyle konur. Uygulama hiçbir koşulda "güvendesin" demez; şüphede acile yönlendirir.

## Fazlar

0. Hazırlık: iskelet, ortam
1. Veri: UCI/Cleveland, MIMIC-IV (başvuru), sentetik panik/reflü/kas ağrısı vakaları, HEART ve EDACS kuralları
2. Model prototipi: HEART kıyas çizgisi, lojistik regresyon, XGBoost, duyarlılık ≥ %98 hedefi
3. Kendini geliştirme: eğit → karşılaştır → daha iyiyse güncelle döngüsü
4. Mobil uygulama: TFLite/ONNX modeli, soru-cevap ekranı
5. Güvenlik ve hukuk (paralel): KVKK, tıbbi cihaz mevzuatı, doktor görüşü

## Gelir yönü (taslak)

Tanı koyan ürün düzenleme gerektirir (TİTCK, CE/FDA). Daha hızlı yol: tanısız triyaj ve panik desteği (yönlendirme, nefes egzersizi, semptom günlüğü), ardından kliniklere B2B. Karar Faz 2 sonuçlarına göre verilecek.

## Yapı

```
data/        ham ve işlenmiş veri (git'e girmez)
notebooks/   keşif
src/         veri hazırlama, eğitim, değerlendirme
models/      eğitilmiş modeller (git'e girmez)
```
