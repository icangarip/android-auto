#!/usr/bin/env python3
"""
TikTok Otomasyon - Locator Versiyonu
Appium server gerektirir!
"""

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

class TikTokWithLocator:
    def __init__(self):
        self.driver = None
        self.wait = None
        
        # Appium server URL
        self.appium_server = 'http://localhost:4723'
        
    def connect(self):
        """Appium ile bağlan"""
        try:
            print("📱 Appium'a bağlanılıyor...")
            
            # Appium ayarları
            options = UiAutomator2Options()
            options.platform_name = 'Android'
            options.device_name = 'Samsung S20'
            options.app_package = 'com.zhiliaoapp.musically'
            options.app_activity = '.MainActivity'
            options.no_reset = True
            options.auto_grant_permissions = True
            
            self.driver = webdriver.Remote(self.appium_server, options=options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Appium bağlantısı başarılı!")
            return True
            
        except Exception as e:
            print(f"❌ Appium bağlantısı başarısız: {e}")
            print("\n⚠️  Appium server'ın açık olduğundan emin olun:")
            print("   Terminal'de: appium")
            return False
    
    def open_tiktok(self):
        """TikTok'u aç veya ön plana getir"""
        try:
            current = self.driver.current_package
            if 'musically' not in current:
                print("🎵 TikTok açılıyor...")
                self.driver.activate_app('com.zhiliaoapp.musically')
                time.sleep(5)
            else:
                print("✅ TikTok zaten açık")
            return True
        except Exception as e:
            print(f"❌ TikTok açılamadı: {e}")
            return False
    
    def like_video_with_locator(self):
        """Locator kullanarak beğen"""
        print("❤️  Like butonu aranıyor (locator ile)...")
        
        # Yöntem 1: Content-Description ile
        try:
            like_btn = self.wait.until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Like"))
            )
            print("✅ Bulundu: content-desc='Like'")
            like_btn.click()
            return True
        except:
            pass
        
        # Yöntem 2: Content-desc varyasyonları
        variations = ["Like", "Like video", "like", "Heart", "Beğen", "Beğeni"]
        for desc in variations:
            try:
                elem = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, desc)
                print(f"✅ Bulundu: content-desc='{desc}'")
                elem.click()
                return True
            except:
                continue
        
        # Yöntem 3: XPath ile
        try:
            xpath = "//android.widget.ImageView[contains(@content-desc, 'Like') or contains(@content-desc, 'like')]"
            like_btn = self.driver.find_element(AppiumBy.XPATH, xpath)
            print("✅ Bulundu: XPath ile")
            like_btn.click()
            return True
        except:
            pass
        
        # Yöntem 4: Resource ID ile (eğer varsa)
        try:
            like_btn = self.driver.find_element(AppiumBy.ID, "com.zhiliaoapp.musically:id/like_button")
            print("✅ Bulundu: Resource ID ile")
            like_btn.click()
            return True
        except:
            pass
        
        print("❌ Like butonu bulunamadı!")
        return False
    
    def swipe_up(self):
        """Sonraki videoya geç"""
        try:
            print("⬆️  Sonraki videoya geçiliyor...")
            size = self.driver.get_window_size()
            
            start_x = size['width'] // 2
            start_y = size['height'] * 0.8
            end_x = size['width'] // 2
            end_y = size['height'] * 0.2
            
            self.driver.swipe(start_x, start_y, end_x, end_y, duration=300)
            return True
        except Exception as e:
            print(f"❌ Kaydırma başarısız: {e}")
            return False
    
    def show_all_locators(self):
        """Sayfadaki tüm locator'ları göster"""
        print("\n🔍 Sayfadaki elementler analiz ediliyor...")
        
        try:
            # Tüm elementleri bul
            elements = self.driver.find_elements(AppiumBy.XPATH, "//*")
            
            found_elements = []
            for elem in elements[:50]:  # İlk 50 element
                try:
                    content_desc = elem.get_attribute("content-desc")
                    resource_id = elem.get_attribute("resourceId")
                    class_name = elem.get_attribute("className")
                    clickable = elem.get_attribute("clickable")
                    
                    if content_desc or resource_id:
                        found_elements.append({
                            'content_desc': content_desc,
                            'resource_id': resource_id,
                            'class': class_name,
                            'clickable': clickable == 'true'
                        })
                except:
                    continue
            
            # Önemli elementleri göster
            print("\n📋 Bulunan önemli elementler:")
            for elem in found_elements[:15]:
                if elem['clickable']:
                    if elem['content_desc']:
                        print(f"  🔘 content-desc: '{elem['content_desc']}'")
                    if elem['resource_id']:
                        print(f"  🔘 resource-id: '{elem['resource_id']}'")
            
            return found_elements
            
        except Exception as e:
            print(f"❌ Element analizi başarısız: {e}")
            return []
    
    def run(self):
        """Ana otomasyon"""
        print("\n🚀 TikTok Locator Otomasyon Başlıyor")
        print("=" * 40)
        
        # 1. Appium bağlantısı
        if not self.connect():
            return False
        
        # 2. TikTok'u aç
        if not self.open_tiktok():
            self.driver.quit()
            return False
        
        # 3. Elementleri göster (debug için)
        self.show_all_locators()
        
        # 4. İlk videoyu izle
        print("\n📺 İlk video 5 saniye izleniyor...")
        time.sleep(5)
        
        # 5. Sonraki videoya geç
        if not self.swipe_up():
            self.driver.quit()
            return False
        
        # 6. Yeni video yüklensin
        print("⏳ Yeni video yükleniyor (2 saniye)...")
        time.sleep(2)
        
        # 7. Locator ile beğen
        if not self.like_video_with_locator():
            print("⚠️  Beğeni yapılamadı ama devam ediliyor...")
        
        time.sleep(1)
        
        print("\n✅ Otomasyon tamamlandı!")
        print("📊 Özet: Locator kullanılarak otomasyon yapıldı")
        
        # Temizlik
        self.driver.quit()
        return True

def main():
    print("🤖 TikTok Locator Otomasyon")
    print("=" * 40)
    print("⚠️  DİKKAT: Bu script Appium server gerektirir!")
    print("\nÖnce Appium'u başlatın:")
    print("   Terminal'de: appium")
    print("\nSonra bu scripti çalıştırın.")
    print()
    
    # Appium kontrolü
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 4723))
    sock.close()
    
    if result != 0:
        print("❌ Appium server açık değil!")
        print("   Önce 'appium' komutunu çalıştırın")
        sys.exit(1)
    
    print("✅ Appium server tespit edildi")
    print("📌 Otomasyon başlatılıyor...\n")
    
    automation = TikTokWithLocator()
    success = automation.run()
    
    if not success:
        print("\n⚠️  Otomasyon tamamlanamadı!")
        sys.exit(1)

if __name__ == "__main__":
    main()