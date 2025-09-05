#!/bin/bash
echo "=== ADB Kurulumu ==="

# ADB kurulu mu kontrol et
if command -v adb &> /dev/null; then
    echo "✅ ADB zaten kurulu"
    adb version
else
    echo "ADB kuruluyor..."
    
    # Ubuntu/Debian için
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y android-tools-adb
    # Arch için  
    elif command -v pacman &> /dev/null; then
        sudo pacman -S android-tools
    else
        echo "❌ Desteklenmeyen Linux dağıtımı"
        echo "Manuel kurulum:"
        echo "Ubuntu/Debian: sudo apt install android-tools-adb"
        echo "Arch: sudo pacman -S android-tools"
        exit 1
    fi
fi

echo ""
echo "=== Alternatif: Windows ADB'yi WSL'den kullanma ==="
echo "Windows ADB yolunu test et:"

WINDOWS_ADB="/mnt/c/Users/canga/Desktop/platform-tools/adb.exe"
if [ -f "$WINDOWS_ADB" ]; then
    echo "✅ Windows ADB bulundu: $WINDOWS_ADB"
    echo "Test ediliyor..."
    "$WINDOWS_ADB" version
else
    echo "❌ Windows ADB bulunamadı: $WINDOWS_ADB"
    echo "Doğru yol: /mnt/c/Users/canga/Desktop/platform-tools/adb.exe"
fi