# Hızlı Çalıştırma Notları

Bu not, locator tabanlı ana botu en kısa yoldan çalıştırmak için özet adımları içerir.

## 0) Appium'u Başlat (Windows)
- Terminal (PowerShell): `appium -a 0.0.0.0 -p 4723`
- Appium çıktısında görünen IP/port erişilebilir olmalı (örn: `http://100.75.55.92:4723`).

## 1) En Kısa Yol (WSL)
- Varsayılan çalışma (2 dk):
  - `make run`
- Hızlı deneme (kısa izleme/daha hızlı akış):
  - `make run-fast`
- Süreyi değiştirmek (ör. 5 dk):
  - `MINS=5 make run`

Not: `make` yoksa aşağıdaki script'i kullanın.

## 2) Script ile (make olmadan)
- 2 dk varsayılan çalışma (server/paket otomatik bulunur):
  - `bash scripts/run_locator.sh -m 2`
- Gerekirse server/paket belirt:
  - `bash scripts/run_locator.sh -s http://100.75.55.92:4723 -p com.zhiliaoapp.musically -m 2`
- Hızlı mod (kısa izleme/smoke):
  - `bash scripts/run_locator.sh -m 2 --fast`

Script ne yapar:
- Appium server adresini otomatik tespit (WSL→Windows IP) etmeye çalışır.
- TikTok paketi için adb üzerinden `musically`/`trill` kontrol eder.
- `.env` varsa içindeki değişkenleri yükler.

## 3) Çıktılar ve Kayıtlar
- Oturum klasörü: `sessions/locator_<timestamp>/`
  - Log: `logs/session.log`
  - Beğenilen videoların ekran görüntüleri: `screenshots/liked_video_###.png`
  - Rapor: `session_report.json` (desc/title, matched keywords, like reason: keywords/random)

## 4) Hızlı Sorun Giderme
- Server testi: `curl -sS $APPIUM_SERVER/status`
- IP erişimi yoksa Appium başlık çıktısındaki diğer URL'yi `-s` ile verin.
- Paket algılanamadıysa `-p com.zhiliaoapp.musically` (veya `com.ss.android.ugc.trill`) girin.
