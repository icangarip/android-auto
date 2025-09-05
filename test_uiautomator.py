#!/usr/bin/env python3
"""
UIAutomator Dump Test
Ekrandaki tüm elementleri ve verilerini gösterir
"""

import subprocess
import time
import xml.etree.ElementTree as ET
import re

def test_uiautomator():
    adb_path = "/mnt/c/Users/canga/Desktop/platform-tools/adb.exe"
    
    print("🔍 UIAutomator Dump Test")
    print("=" * 50)
    
    # 1. UI dump al
    print("\n📸 UI dump alınıyor...")
    result = subprocess.run(
        [adb_path, 'shell', 'uiautomator', 'dump', '/sdcard/ui_dump.xml'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Dump alınamadı: {result.stderr}")
        return
    
    print("✅ UI dump başarılı")
    time.sleep(0.5)
    
    # 2. XML'i oku
    print("\n📖 XML okunuyor...")
    xml_result = subprocess.run(
        [adb_path, 'shell', 'cat', '/sdcard/ui_dump.xml'],
        capture_output=True,
        text=True
    )
    
    if xml_result.returncode != 0:
        print(f"❌ XML okunamadı: {xml_result.stderr}")
        return
    
    xml_content = xml_result.stdout
    print(f"✅ XML boyutu: {len(xml_content)} karakter")
    
    # 3. XML'i parse et
    print("\n🔬 Elementler analiz ediliyor...")
    try:
        root = ET.fromstring(xml_content)
        
        # Tüm elementleri topla
        all_elements = []
        clickable_elements = []
        text_elements = []
        time_elements = []
        
        for elem in root.iter('node'):
            # Element özellikleri
            text = elem.get('text', '')
            content_desc = elem.get('content-desc', '')
            resource_id = elem.get('resource-id', '')
            class_name = elem.get('class', '')
            clickable = elem.get('clickable', 'false')
            bounds = elem.get('bounds', '')
            
            # Boş olmayanları kaydet
            if text or content_desc or resource_id:
                element_info = {
                    'text': text,
                    'content_desc': content_desc,
                    'resource_id': resource_id,
                    'class': class_name,
                    'clickable': clickable == 'true',
                    'bounds': bounds
                }
                all_elements.append(element_info)
                
                # Tıklanabilir elementler
                if clickable == 'true':
                    clickable_elements.append(element_info)
                
                # Text içeren elementler
                if text:
                    text_elements.append(element_info)
                    
                    # Zaman formatı içerenler (0:15, 1:23 gibi)
                    if re.match(r'\d{1,2}:\d{2}', text):
                        time_elements.append(element_info)
        
        # 4. Sonuçları göster
        print(f"\n📊 ÖZET:")
        print(f"• Toplam element: {len(list(root.iter('node')))}")
        print(f"• İçerikli element: {len(all_elements)}")
        print(f"• Tıklanabilir: {len(clickable_elements)}")
        print(f"• Text içeren: {len(text_elements)}")
        print(f"• Zaman formatında: {len(time_elements)}")
        
        # 5. Önemli elementleri listele
        if time_elements:
            print(f"\n⏱️ ZAMAN İÇEREN ELEMENTLER:")
            for elem in time_elements:
                print(f"  • Text: '{elem['text']}'")
                print(f"    Bounds: {elem['bounds']}")
                print(f"    Class: {elem['class']}")
        
        print(f"\n📝 İLK 10 TEXT ELEMENT:")
        for i, elem in enumerate(text_elements[:10], 1):
            print(f"  {i}. '{elem['text'][:50]}{'...' if len(elem['text']) > 50 else ''}'")
            if elem['resource_id']:
                print(f"     ID: {elem['resource_id']}")
        
        print(f"\n🎯 TIKLANABILIR ELEMENTLER (content-desc):")
        seen_descs = set()
        for elem in clickable_elements:
            if elem['content_desc'] and elem['content_desc'] not in seen_descs:
                seen_descs.add(elem['content_desc'])
                print(f"  • '{elem['content_desc']}'")
                # Koordinatları parse et
                if elem['bounds']:
                    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', elem['bounds'])
                    if match:
                        x1, y1, x2, y2 = map(int, match.groups())
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        print(f"    Merkez: ({center_x}, {center_y})")
        
        # 6. TikTok'a özel elementleri ara
        print(f"\n🎵 TIKTOK ÖZELLİKLERİ:")
        tiktok_keywords = ['like', 'Like', 'comment', 'Comment', 'share', 'Share', 
                          'follow', 'Follow', 'music', 'Music', 'beğen', 'Beğen',
                          'yorum', 'Yorum', 'paylaş', 'Paylaş']
        
        for elem in all_elements:
            for keyword in tiktok_keywords:
                if keyword in elem.get('content_desc', '').lower() or \
                   keyword in elem.get('text', '').lower() or \
                   keyword in elem.get('resource_id', '').lower():
                    print(f"  ✓ {keyword.capitalize()} bulundu:")
                    if elem['content_desc']:
                        print(f"    Content-desc: '{elem['content_desc']}'")
                    if elem['text']:
                        print(f"    Text: '{elem['text']}'")
                    if elem['resource_id']:
                        print(f"    ID: '{elem['resource_id']}'")
                    break
        
        # 7. Ham XML örneği
        print(f"\n📄 HAM XML ÖRNEĞİ (ilk 500 karakter):")
        print("-" * 50)
        print(xml_content[:500])
        print("-" * 50)
        
    except ET.ParseError as e:
        print(f"❌ XML parse hatası: {e}")
        print("\n📄 Ham içerik (ilk 1000 karakter):")
        print(xml_content[:1000])
    
    # 8. Temizlik
    print("\n🧹 Temp dosya siliniyor...")
    subprocess.run([adb_path, 'shell', 'rm', '/sdcard/ui_dump.xml'])
    print("✅ Test tamamlandı!")

if __name__ == "__main__":
    test_uiautomator()