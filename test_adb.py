#!/usr/bin/env python3
import subprocess
import sys

def run_adb_command(command):
    """ADB komutu çalıştır"""
    adb_path = "/mnt/c/Users/canga/Desktop/platform-tools/adb.exe"
    full_command = [adb_path] + command
    try:
        result = subprocess.run(full_command, capture_output=True, text=True)
        print(f"Komut: {' '.join(full_command)}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"Hata: {e}")
        return False, "", str(e)

def main():
    print("=== ADB Bağlantı Testi ===\n")
    
    # 1. ADB cihazları listele
    print("1. Bağlı cihazları kontrol et:")
    success, output, error = run_adb_command(['devices'])
    if not success:
        print("❌ ADB çalışmıyor!")
        return
    print("✅ ADB çalışıyor\n")
    
    # 2. Ekran boyutunu al
    print("2. Ekran boyutunu kontrol et:")
    success, output, error = run_adb_command(['shell', 'wm', 'size'])
    if success and output:
        print(f"✅ Ekran boyutu: {output.strip()}")
    else:
        print("❌ Ekran boyutu alınamadı")
    print()
    
    # 3. Yoğunluk kontrol et
    print("3. Ekran yoğunluğunu kontrol et:")
    success, output, error = run_adb_command(['shell', 'wm', 'density'])
    if success and output:
        print(f"✅ Yoğunluk: {output.strip()}")
    print()
    
    # 4. TikTok kurulu mu kontrol et
    print("4. TikTok kurulu mu kontrol et:")
    success, output, error = run_adb_command(['shell', 'pm', 'list', 'packages', 'trill'])
    if success and 'com.ss.android.ugc.trill' in output:
        print("✅ TikTok kurulu")
    else:
        print("❌ TikTok bulunamadı")
        print("TikTok paket adı kontrol ediliyor...")
        success, output, error = run_adb_command(['shell', 'pm', 'list', 'packages', 'tiktok'])
        if success and output:
            print(f"TikTok benzeri paketler: {output}")
    print()
    
    # 5. Test dokunuşu yap
    print("5. Test dokunuşu yap (ekran ortası):")
    success, output, error = run_adb_command(['shell', 'input', 'tap', '500', '1000'])
    if success:
        print("✅ Dokunuş başarılı")
    else:
        print("❌ Dokunuş başarısız")
    print()
    
    print("=== Test Tamamlandı ===")
    print("Şimdi TikTok otomasyonunu test edebilirsiniz!")

if __name__ == "__main__":
    main()