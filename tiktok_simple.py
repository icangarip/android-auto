#!/usr/bin/env python3
"""
Basit TikTok Otomasyon Scripti
- TikTok'u açar
- İlk videoyu 5 saniye izler
- Bir sonraki videoya geçer
- O videoyu beğenir
- Çıkar
"""

import subprocess
import time
import sys

class SimpleTikTok:
    def __init__(self):
        # Windows ADB path (WSL'den erişim)
        self.adb_path = "/mnt/c/Users/canga/Desktop/platform-tools/adb.exe"
        
        # TikTok koordinatları (Appium Inspector ile bulundu)
        self.like_button = (994, 1136)
        
        # Swipe koordinatları
        self.swipe_start = (540, 1800)
        self.swipe_end = (540, 800)
        
    def adb_command(self, command):
        """ADB komutu çalıştır"""
        full_command = [self.adb_path] + command
        try:
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                print(f"⚠️  ADB Hatası: {result.stderr}")
                return False
            return True
        except subprocess.TimeoutExpired:
            print("⏱️  ADB komutu zaman aşımına uğradı")
            return False
        except Exception as e:
            print(f"❌ Hata: {e}")
            return False
    
    def check_device(self):
        """Cihaz bağlantısını kontrol et"""
        print("📱 Cihaz kontrol ediliyor...")
        if self.adb_command(['devices']):
            result = subprocess.run([self.adb_path, 'devices'], capture_output=True, text=True)
            devices = result.stdout.strip().split('\n')[1:]  # İlk satır başlık
            if devices and devices[0].strip():
                print("✅ Cihaz bağlandı!")
                return True
        print("❌ Cihaz bulunamadı! Telefonu USB ile bağlayın ve USB hata ayıklamayı açın.")
        return False
    
    def open_tiktok(self):
        """TikTok'u aç"""
        print("🎵 TikTok açılıyor...")
        return self.adb_command([
            'shell', 'monkey', '-p', 'com.zhiliaoapp.musically', 
            '-c', 'android.intent.category.LAUNCHER', '1'
        ])
    
    def tap(self, x, y):
        """Ekrana dokun"""
        return self.adb_command(['shell', 'input', 'tap', str(x), str(y)])
    
    def swipe_up(self):
        """Yukarı kaydır (sonraki video)"""
        print("⬆️  Sonraki videoya geçiliyor...")
        return self.adb_command([
            'shell', 'input', 'swipe',
            str(self.swipe_start[0]), str(self.swipe_start[1]),
            str(self.swipe_end[0]), str(self.swipe_end[1]),
            '300'  # 300ms sürede kaydır
        ])
    
    def like_video(self):
        """Videoyu beğen"""
        print("❤️  Video beğeniliyor...")
        return self.tap(self.like_button[0], self.like_button[1])
    
    def run(self):
        """Ana otomasyon"""
        print("\n🚀 TikTok Basit Otomasyon Başlıyor")
        print("=" * 40)
        
        # 1. Cihaz kontrolü
        if not self.check_device():
            return False
        
        # 2. TikTok'u aç
        if not self.open_tiktok():
            print("❌ TikTok açılamadı!")
            return False
        
        # 3. Uygulama yüklenmesi için bekle
        print("⏳ TikTok yükleniyor (5 saniye)...")
        time.sleep(5)
        
        # 4. İlk videoyu izle
        print("\n📺 İlk video 5 saniye izleniyor...")
        time.sleep(5)
        
        # 5. Sonraki videoya geç
        if not self.swipe_up():
            print("❌ Kaydırma başarısız!")
            return False
        
        # 6. Yeni videonun yüklenmesini bekle
        print("⏳ Yeni video yükleniyor (2 saniye)...")
        time.sleep(2)
        
        # 7. İkinci videoyu beğen
        if not self.like_video():
            print("❌ Beğenme başarısız!")
            return False
        
        # 8. Biraz bekle
        time.sleep(1)
        
        print("\n✅ Otomasyon tamamlandı!")
        print("📊 Özet: 2 video izlendi, 1 video beğenildi")
        return True

def main():
    print("🤖 TikTok Basit Otomasyon")
    print("=" * 40)
    print("Bu script:")
    print("1. TikTok'u açar")
    print("2. İlk videoyu 5 saniye izler")
    print("3. Sonraki videoya geçer")
    print("4. O videoyu beğenir")
    print("5. Çıkar")
    print()
    
    # input("Başlamak için ENTER'a basın...")  # Test için kapatıldı
    print("📌 Otomatik başlatılıyor...")
    
    automation = SimpleTikTok()
    success = automation.run()
    
    if not success:
        print("\n⚠️  Otomasyon tamamlanamadı!")
        print("Kontrol listesi:")
        print("1. Telefon USB ile bağlı mı?")
        print("2. USB hata ayıklama açık mı?")
        print("3. TikTok yüklü mü?")
        print("4. ADB yolu doğru mu?")
        sys.exit(1)

if __name__ == "__main__":
    main()