# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Android automation project focused on TikTok interaction via ADB and Appium. The codebase provides both direct ADB-based automation and Appium WebDriver-based automation for controlling an Android device from WSL/Linux.

## Development Commands

### Run TikTok Automation
```bash
# Direct ADB automation (uses Windows ADB from WSL)
python3 tiktok_automation.py

# Appium-based automation (requires Appium server running)
python3 appium_tiktok_automation.py
```

### Setup Commands
```bash
# Install ADB (checks for existing installation)
./install_adb.sh

# Install Appium server and drivers
./install_appium.sh

# Start Appium server (required for Appium automation)
appium
```

### Testing Specific Components
```bash
# Test ADB connection
python3 test_adb.py

# Test Appium connection
python3 test_appium_connection.py

# Quick 1-minute test
python3 quick_test_1min.py

# Find UI coordinates
python3 find_coordinates.py
```

## Architecture

### ADB Path Configuration
The project uses Windows ADB from WSL. The standard path is:
```
/mnt/c/Users/canga/Desktop/platform-tools/adb.exe
```

### Key Coordinates (Samsung S20)
- Screen dimensions: 1080x2400
- Like button: (994, 1136)
- Comment button: (964, 1344)
- Swipe area: start (540, 1800) to end (540, 800)

### Automation Approaches

1. **Direct ADB (`tiktok_automation.py`)**: Uses subprocess calls to Windows ADB for tap, swipe, and keyevent commands. Includes randomization for natural behavior.

2. **Appium WebDriver (`appium_tiktok_automation.py`)**: Uses Appium Python Client with UiAutomator2 for element detection via content-desc, XPath, and class names. Connects to Appium server on localhost:4723.

### TikTok Package Information
- Package: `com.zhiliaoapp.musically`
- Main Activity: `.MainActivity`

## Dependencies

- Python packages: `Appium-Python-Client` (5.2.2)
- Appium server with UiAutomator2 driver
- Windows ADB accessible from WSL