#!/usr/bin/env python3
"""
UIAutomator dump'ın tamamını göster
"""

import subprocess
import time

def main():
    adb_path = "/mnt/c/Users/canga/Desktop/platform-tools/adb.exe"
    
    print("📸 UIAutomator Full Dump")
    print("=" * 50)
    
    # 1. UI dump al
    print("Dump alınıyor...")
    subprocess.run(
        [adb_path, 'shell', 'uiautomator', 'dump', '/sdcard/full_dump.xml'],
        capture_output=True,
        text=True
    )
    time.sleep(0.5)
    
    # 2. XML'i oku ve göster
    print("\n" + "="*50)
    print("FULL XML DUMP:")
    print("="*50 + "\n")
    
    result = subprocess.run(
        [adb_path, 'shell', 'cat', '/sdcard/full_dump.xml'],
        capture_output=True,
        text=True
    )
    
    # Tamamını yazdır
    xml_content = result.stdout
    print(xml_content)
    
    # İstatistik
    print("\n" + "="*50)
    print(f"Toplam karakter: {len(xml_content)}")
    print(f"Toplam satır: {len(xml_content.splitlines())}")
    print("="*50)
    
    # Dosyayı local'e de kaydet
    with open('tiktok_full_dump.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    print("\n✅ Dump 'tiktok_full_dump.xml' dosyasına kaydedildi")
    
    # Temizlik
    subprocess.run([adb_path, 'shell', 'rm', '/sdcard/full_dump.xml'])

if __name__ == "__main__":
    main()