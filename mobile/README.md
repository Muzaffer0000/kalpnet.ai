# KalpNet mobil (Expo / React Native)

`app/` altındaki PWA'nın Expo / React Native sürümü. **Tıbbi cihaz değildir**, sentetik veriyle eğitilmiştir ve girdiğiniz bilgiler cihazdan dışarı çıkmaz.

## Kurulum
```
cd mobile
npm install
```

## Yeniden eğitimden sonra
Otomatik `prestart` kancası yok; senkronizasyon elle yapılır:
```
python src/export_model.py
python tests/make_parity_fixture.py
cd mobile && npm run sync-model
cd .. && node tests/test_mobile_parity.mjs
```

## Çalıştırma
```
npx expo start
```
QR kodunu Expo Go ile okutun (telefon ve bilgisayar aynı Wi-Fi'de olmalı). Olmuyorsa: `npx expo start --tunnel`.

## Testler
```
node tests/test_mobile_parity.mjs          # repo kökünden
node --test mobile/src/validate.test.mjs
```
Test edilenler: 200 vakada skor eşliği (PWA ile aynı sonuç), `score.js` / `model.json` kopyalarının `app/` ile byte-aynı olması, girdi doğrulama (eksik cevap, yaş/süre sınırları, kontrol sırası).

Test EDİLMEYENLER (elle kontrol gerekir): arayüz görünümü, gerçek cihaz davranışı, `tel:` (112) bağlantısı, animasyon (nefes egzersizi), erişilebilirlik.

## Mağaza notları
- Google Play: tek seferlik 25 USD geliştirici ücreti. Apple Developer Program: yıllık 99 USD.
- Sağlık uygulamaları daha sıkı incelenir (tıbbi iddialar, uyarı metinleri).
- Herhangi bir başvurudan önce Faz 5 hukuki/düzenleyici inceleme (ör. tıbbi cihaz sınıflandırması, KVKK) tamamlanmalıdır.
