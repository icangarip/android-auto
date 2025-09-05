#!/usr/bin/env python3
"""
TikTok Akıllı Süre Tespiti
Video süresini farklı yöntemlerle tespit eder
"""

import subprocess
import time
import re
import random

class SmartTikTok:
    def __init__(self):
        self.adb_path = "/mnt/c/Users/canga/Desktop/platform-tools/adb.exe"
        self.like_button = (994, 1136)
        self.swipe_start = (540, 1800)
        self.swipe_end = (540, 800)
        
    def adb_command(self, command):
        """ADB komutu çalıştır"""
        full_command = [self.adb_path] + command
        try:
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=5)
            return result.stdout if result.returncode == 0 else None
        except:
            return None
    
    def find_duration_with_uiautomator(self):
        """UIAutomator ile süre bulmayı dene"""
        print("🔍 Video süresi aranıyor (UIAutomator)...")
        
        # UI dump al
        self.adb_command(['shell', 'uiautomator', 'dump', '/sdcard/ui_dump.xml'])
        time.sleep(0.5)
        
        # XML'i oku
        xml_content = self.adb_command(['shell', 'cat', '/sdcard/ui_dump.xml'])
        
        if xml_content:
            # Süre formatlarını ara: "0:15", "1:23", "00:45" vb.
            duration_patterns = [
                r'\b\d{1,2}:\d{2}\b',  # 0:15, 1:23
                r'\b\d{2}:\d{2}\b',     # 00:15, 01:23
            ]
            
            for pattern in duration_patterns:
                matches = re.findall(pattern, xml_content)
                if matches:
                    # En kısa süreyi al (genelde video süresi)
                    durations = []
                    for match in matches:
                        parts = match.split(':')
                        seconds = int(parts[0]) * 60 + int(parts[1])
                        if 5 <= seconds <= 180:  # 5 saniye - 3 dakika arası
                            durations.append((match, seconds))
                    
                    if durations:
                        duration_text, seconds = min(durations, key=lambda x: x[1])
                        print(f"✅ Süre bulundu: {duration_text} ({seconds} saniye)")
                        return seconds
        
        print("❌ Süre bulunamadı")
        return None
    
    def detect_video_loop(self, max_wait=60):
        """Video tekrarını tespit ederek süreyi bul"""
        print("🔄 Video döngüsü tespiti...")
        
        start_time = time.time()
        first_screenshot = f"/sdcard/first_{int(time.time())}.png"
        
        # İlk ekran görüntüsünü al
        self.adb_command(['shell', 'screencap', '-p', first_screenshot])
        time.sleep(2)
        
        while time.time() - start_time < max_wait:
            current_screenshot = f"/sdcard/current_{int(time.time())}.png"
            self.adb_command(['shell', 'screencap', '-p', current_screenshot])
            
            # Görüntüleri karşılaştır (basit boyut karşılaştırması)
            first_size = self.adb_command(['shell', 'stat', '-c', '%s', first_screenshot])
            current_size = self.adb_command(['shell', 'stat', '-c', '%s', current_screenshot])
            
            if first_size and current_size:
                # Boyutlar çok yakınsa video başa dönmüş olabilir
                diff = abs(int(first_size) - int(current_size))
                if diff < 1000:  # 1KB'den az fark
                    duration = int(time.time() - start_time)
                    print(f"✅ Video döngüsü tespit edildi: ~{duration} saniye")
                    
                    # Temizlik
                    self.adb_command(['shell', 'rm', first_screenshot])
                    self.adb_command(['shell', 'rm', current_screenshot])
                    return duration
            
            time.sleep(2)
        
        print("⏱️ Video döngüsü tespit edilemedi, maksimum süre aşıldı")
        return None
    
    def smart_watch_video(self):
        """Akıllı video izleme"""
        print("\n📺 Video analiz ediliyor...")
        
        # Yöntem 1: UIAutomator ile süre bul
        duration = self.find_duration_with_uiautomator()
        
        if duration:
            # Sürenin %60-90'ını izle
            watch_percentage = random.uniform(0.6, 0.9)
            watch_time = min(duration * watch_percentage, 30)  # Max 30 saniye
            print(f"⏰ {watch_time:.1f} saniye izlenecek (videonun %{watch_percentage*100:.0f}'ı)")
            time.sleep(watch_time)
            return True
        
        # Yöntem 2: Sabit süre aralığı
        print("💭 Süre bulunamadı, rastgele süre kullanılıyor...")
        
        # TikTok videoları genelde 15-60 saniye
        common_durations = [15, 20, 25, 30, 45, 60]
        weights = [0.3, 0.25, 0.2, 0.15, 0.05, 0.05]  # Olasılık ağırlıkları
        
        estimated_duration = random.choices(common_durations, weights=weights)[0]
        watch_percentage = random.uniform(0.5, 0.8)
        watch_time = estimated_duration * watch_percentage
        
        print(f"📊 Tahmini süre: {estimated_duration}s, izlenecek: {watch_time:.1f}s")
        time.sleep(watch_time)
        return True
    
    def double_tap_like(self):
        """Çift tıklama ile beğeni (alternatif)"""
        print("👆👆 Çift tıklama ile beğeni...")
        center_x = 540
        center_y = 1200
        
        # Hızlı iki tıklama
        self.adb_command(['shell', 'input', 'tap', str(center_x), str(center_y)])
        time.sleep(0.1)
        self.adb_command(['shell', 'input', 'tap', str(center_x), str(center_y)])
        return True
    
    def swipe_up(self):
        """Sonraki videoya geç"""
        print("⬆️ Sonraki video...")
        return self.adb_command([
            'shell', 'input', 'swipe',
            str(self.swipe_start[0]), str(self.swipe_start[1]),
            str(self.swipe_end[0]), str(self.swipe_end[1]),
            '300'
        ]) is not None
    
    def run_smart_session(self, video_count=5):
        """Akıllı oturum"""
        print(f"\n🚀 Akıllı TikTok Otomasyonu ({video_count} video)")
        print("=" * 50)
        
        # TikTok'u aç
        print("🎵 TikTok açılıyor...")
        self.adb_command([
            'shell', 'monkey', '-p', 'com.zhiliaoapp.musically',
            '-c', 'android.intent.category.LAUNCHER', '1'
        ])
        time.sleep(5)
        
        for i in range(1, video_count + 1):
            print(f"\n--- Video {i}/{video_count} ---")
            
            # Akıllı izleme
            self.smart_watch_video()
            
            # Rastgele beğeni (%30 şans)
            if random.random() < 0.3:
                # %50 normal beğeni, %50 çift tıklama
                if random.random() < 0.5:
                    print("❤️ Normal beğeni...")
                    self.adb_command(['shell', 'input', 'tap', str(self.like_button[0]), str(self.like_button[1])])
                else:
                    self.double_tap_like()
                time.sleep(1)
            
            # Son video değilse kaydır
            if i < video_count:
                self.swipe_up()
                time.sleep(random.uniform(1, 3))
        
        print("\n✅ Akıllı oturum tamamlandı!")
        return True

def main():
    print("🧠 TikTok Akıllı Süre Otomasyonu")
    print("=" * 40)
    print("\nÖzellikler:")
    print("• Video süresini otomatik tespit")
    print("• Akıllı izleme süresi")
    print("• Rastgele davranışlar")
    print("• Çift tıklama beğeni")
    print()
    
    automation = SmartTikTok()
    
    print("1. Hızlı test (3 video)")
    print("2. Normal oturum (5 video)")
    print("3. Uzun oturum (10 video)")
    
    choice = input("\nSeçiminiz (1-3): ")
    
    if choice == "1":
        automation.run_smart_session(3)
    elif choice == "2":
        automation.run_smart_session(5)
    elif choice == "3":
        automation.run_smart_session(10)
    else:
        # Default
        automation.run_smart_session(5)

if __name__ == "__main__":
    main()