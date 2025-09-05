#!/usr/bin/env python3
import subprocess

def run_adb(command):
    adb_path = "/mnt/c/Users/canga/Desktop/platform-tools/adb.exe"
    full_command = [adb_path, 'shell'] + command
    result = subprocess.run(full_command, capture_output=True, text=True)
    return result.stdout.strip()

def enable_show_touches():
    """Make touches visible"""
    print("Enabling visible touches...")
    run_adb(['settings', 'put', 'system', 'show_touches', '1'])
    print("✅ Now you can see where you touch")

def disable_show_touches():
    """Hide touches"""
    print("Disabling visible touches...")
    run_adb(['settings', 'put', 'system', 'show_touches', '0'])
    print("✅ Touches are now hidden")

def test_coordinates():
    """Manual coordinate testing"""
    print("=== Coordinate Test ===")
    print("Open TikTok and run this test while watching a video\n")
    
    # Test koordinatları
    test_points = [
        ("Screen center", 540, 1200),
        ("Right bottom - like button (estimate)", 950, 1600),
        ("Right bottom - comment button (estimate)", 950, 1700),
        ("Right bottom - share button (estimate)", 950, 1800),
        ("Left bottom - profile (estimate)", 150, 1900),
    ]
    
    for name, x, y in test_points:
        input(f"\nTest: {name} ({x}, {y}) - Press ENTER...")
        run_adb(['input', 'tap', str(x), str(y)])
        print(f"✅ Tapped {name} coordinate")
    
    print("\nWhich coordinates worked correctly?")

def main():
    print("=== TikTok Coordinate Finder ===\n")
    print("1. Make touches visible (for testing)")
    print("2. Run coordinate test")
    print("3. Hide touches")
    print("4. Manual coordinate input")
    
    choice = input("\nYour choice (1-4): ")
    
    if choice == "1":
        enable_show_touches()
    elif choice == "2":
        test_coordinates()
    elif choice == "3":
        disable_show_touches()
    elif choice == "4":
        print("\nManual test:")
        x = input("X coordinate: ")
        y = input("Y coordinate: ")
        run_adb(['input', 'tap', x, y])
        print(f"✅ Tapped coordinate ({x}, {y})")

if __name__ == "__main__":
    main()