# Göğüs Ağrısı Ön Değerlendirme (PWA)

Bağımlılıksız, derleme adımsız statik uygulama. Skor, `model.json` içindeki lojistik regresyon
parametreleriyle tarayıcıda hesaplanır; hiçbir veri cihazdan çıkmaz.
**Tıbbi cihaz değildir, tanı koymaz; sentetik veriyle eğitilmiş bir prototiptir.**

## Telefonda açma
- **Aynı Wi-Fi:** bilgisayarda `.venv/Scripts/python -m http.server 8765 --directory app` çalıştırın,
  telefondan `http://<bilgisayarın-IP-adresi>:8765` adresini açın. (Not: "Ana ekrana ekle" ve çevrimdışı mod
  için HTTPS gerekir; yerel IP üzerinde uygulama çalışır ama servis çalışanı kayıt olmayabilir.)
- **GitHub Pages:** depoda Settings > Pages > kaynak olarak `app` klasörünü (veya bir `gh-pages` dalını) seçin.
  HTTPS olduğu için telefonda "Ana ekrana ekle" ve çevrimdışı kullanım çalışır.

## Model yeniden eğitildikten sonra
```
python src/export_model.py              # app/model.json'ı günceller
python tests/make_parity_fixture.py     # Python/JS eşitlik verisini yeniler
node tests/test_app_parity.mjs          # JS skorları Python ile aynı mı?
```
Önbellekli eski sürüm görünürse `sw.js` içindeki `V` sürümünü artırın.
