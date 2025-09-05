#!/usr/bin/env python3
"""
TikTok'u aç ve UIAutomator dump al
"""

import subprocess
import time
import xml.etree.ElementTree as ET
import re

def main():
    adb_path = "/mnt/c/Users/canga/Desktop/platform-tools/adb.exe"
    
    print("🎵 TikTok açılıyor ve UI dump alınıyor")
    print("=" * 50)
    
    # 1. TikTok'u aç
    print("\n📱 TikTok başlatılıyor...")
    result = subprocess.run(
        [adb_path, 'shell', 'monkey', '-p', 'com.zhiliaoapp.musically', 
         '-c', 'android.intent.category.LAUNCHER', '1'],
        capture_output=True,
        text=True
    )
    
    if "Events injected: 1" in result.stdout:
        print("✅ TikTok açıldı")
    else:
        print("⚠️ TikTok açılırken sorun oldu")
    
    # 2. TikTok'un yüklenmesini bekle
    print("⏳ TikTok yükleniyor (7 saniye)...")
    time.sleep(7)
    
    # 3. UI dump al
    print("\n📸 UI dump alınıyor...")
    subprocess.run(
        [adb_path, 'shell', 'uiautomator', 'dump', '/sdcard/tiktok_dump.xml'],
        capture_output=True,
        text=True
    )
    time.sleep(0.5)
    
    # 4. XML'i oku
    print("📖 TikTok UI verisi okunuyor...")
    xml_result = subprocess.run(
        [adb_path, 'shell', 'cat', '/sdcard/tiktok_dump.xml'],
        capture_output=True,
        text=True
    )
    
    xml_content = xml_result.stdout
    print(f"✅ XML boyutu: {len(xml_content)} karakter")
    
    # 5. Parse et ve analiz et
    try:
        root = ET.fromstring(xml_content)
        
        print("\n🔍 TIKTOK UI ANALİZİ:")
        print("-" * 50)
        
        # Video süresi ara
        time_patterns = []
        like_elements = []
        comment_elements = []
        share_elements = []
        music_elements = []
        all_texts = []
        
        for elem in root.iter('node'):
            text = elem.get('text', '')
            content_desc = elem.get('content-desc', '')
            resource_id = elem.get('resource-id', '')
            bounds = elem.get('bounds', '')
            clickable = elem.get('clickable', 'false')
            
            # Text içerenler
            if text:
                all_texts.append({
                    'text': text,
                    'bounds': bounds,
                    'id': resource_id
                })
                
                # Süre formatı
                if re.match(r'^\d{1,2}:\d{2}$', text.strip()):
                    time_patterns.append({
                        'text': text,
                        'bounds': bounds
                    })
            
            # Like button
            if any(word in content_desc.lower() for word in ['like', 'beğen', 'heart', 'kalp']):
                like_elements.append({
                    'desc': content_desc,
                    'bounds': bounds,
                    'clickable': clickable
                })
            
            # Comment button
            if any(word in content_desc.lower() for word in ['comment', 'yorum']):
                comment_elements.append({
                    'desc': content_desc,
                    'bounds': bounds,
                    'clickable': clickable
                })
            
            # Share button
            if any(word in content_desc.lower() for word in ['share', 'paylaş']):
                share_elements.append({
                    'desc': content_desc,
                    'bounds': bounds,
                    'clickable': clickable
                })
            
            # Music info
            if any(word in content_desc.lower() for word in ['music', 'müzik', 'original sound', 'ses']):
                music_elements.append({
                    'desc': content_desc,
                    'text': text,
                    'bounds': bounds
                })
        
        # Sonuçları göster
        if time_patterns:
            print("\n⏱️ VİDEO SÜRESİ BULUNDU:")
            for t in time_patterns:
                print(f"  • Süre: {t['text']}")
                # Koordinatları parse et
                if t['bounds']:
                    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', t['bounds'])
                    if match:
                        x1, y1, x2, y2 = map(int, match.groups())
                        print(f"    Konum: ({(x1+x2)//2}, {(y1+y2)//2})")
        else:
            print("\n⏱️ Video süresi görünmüyor (video oynatılıyor olabilir)")
        
        if like_elements:
            print("\n❤️ LIKE BUTTON:")
            for elem in like_elements[:1]:  # İlkini al
                print(f"  • Content-desc: '{elem['desc']}'")
                if elem['bounds']:
                    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', elem['bounds'])
                    if match:
                        x1, y1, x2, y2 = map(int, match.groups())
                        print(f"    Koordinat: ({(x1+x2)//2}, {(y1+y2)//2})")
                        print(f"    Tıklanabilir: {elem['clickable']}")
        
        if comment_elements:
            print("\n💬 COMMENT BUTTON:")
            for elem in comment_elements[:1]:
                print(f"  • Content-desc: '{elem['desc']}'")
                if elem['bounds']:
                    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', elem['bounds'])
                    if match:
                        x1, y1, x2, y2 = map(int, match.groups())
                        print(f"    Koordinat: ({(x1+x2)//2}, {(y1+y2)//2})")
        
        if share_elements:
            print("\n📤 SHARE BUTTON:")
            for elem in share_elements[:1]:
                print(f"  • Content-desc: '{elem['desc']}'")
                if elem['bounds']:
                    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', elem['bounds'])
                    if match:
                        x1, y1, x2, y2 = map(int, match.groups())
                        print(f"    Koordinat: ({(x1+x2)//2}, {(y1+y2)//2})")
        
        if music_elements:
            print("\n🎵 MÜZİK BİLGİSİ:")
            for elem in music_elements[:1]:
                print(f"  • Content-desc: '{elem['desc']}'")
                if elem['text']:
                    print(f"  • Text: '{elem['text']}'")
        
        # Tüm text'leri göster
        print("\n📝 EKRANDA GÖRÜNEN TEXTLER (ilk 15):")
        for i, t in enumerate(all_texts[:15], 1):
            text_display = t['text'][:50] + ('...' if len(t['text']) > 50 else '')
            print(f"  {i}. '{text_display}'")
            if t['id']:
                print(f"     ID: {t['id']}")
        
        # TikTok package kontrolü
        print("\n📦 PAKET BİLGİSİ:")
        tiktok_found = False
        for elem in root.iter('node'):
            package = elem.get('package', '')
            if 'musically' in package or 'tiktok' in package.lower():
                tiktok_found = True
                print(f"  ✅ TikTok paketi doğrulandı: {package}")
                break
        
        if not tiktok_found:
            print("  ⚠️ TikTok paketi bulunamadı, uygulama açık olmayabilir")
        
    except ET.ParseError as e:
        print(f"❌ XML parse hatası: {e}")
    
    # 6. Temizlik
    print("\n🧹 Temp dosya siliniyor...")
    subprocess.run([adb_path, 'shell', 'rm', '/sdcard/tiktok_dump.xml'])
    print("✅ Analiz tamamlandı!")

if __name__ == "__main__":
    main()