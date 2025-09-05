# 🚀 Appium Inspector Setup Guide for TikTok

## What is Appium Inspector?
- **Visual tool** to see ALL app elements
- **Point & click** to find coordinates
- **Real-time** element inspection
- **XPath, ID, Class** selectors for every element

## 🎯 What You Can Find with Appium:
- ✅ **Exact coordinates** of like button
- ✅ **Video duration** if displayed
- ✅ **All clickable elements**
- ✅ **Hidden elements** UIAutomator can't see
- ✅ **Element IDs** for automation

## 📦 Quick Setup (Windows):

### 1. Install Node.js
```bash
# Download from https://nodejs.org/
# Or with chocolatey:
choco install nodejs
```

### 2. Install Appium
```cmd
npm install -g appium
npm install -g appium-doctor
```

### 3. Install Appium Inspector
- Download from: https://github.com/appium/appium-inspector/releases
- Choose: `Appium-Inspector-windows-*.exe`
- Just run it - no installation needed!

### 4. Install Appium UiAutomator2 Driver
```cmd
appium driver install uiautomator2
```

## 🔧 Configuration:

### Start Appium Server:
```cmd
appium
```
Default port: 4723

### Appium Inspector Settings:
```json
{
  "platformName": "Android",
  "appium:deviceName": "Samsung S20",
  "appium:automationName": "UiAutomator2",
  "appium:appPackage": "com.zhiliaoapp.musically",
  "appium:appActivity": ".MainActivity",
  "appium:noReset": true
}
```

## 🎮 How to Use:

1. **Start Appium server**: `appium`
2. **Open Appium Inspector**
3. **Set Remote Host**: `127.0.0.1`
4. **Set Remote Port**: `4723`
5. **Enter capabilities** (above JSON)
6. **Click "Start Session"**

## 🔍 Finding Elements in TikTok:

### In Appium Inspector:
- **Click any element** - shows all properties
- **See coordinates** instantly
- **Find by ID**: `com.zhiliaoapp.musically:id/like_button`
- **Find by XPath**: `//android.widget.Button[@content-desc="Like"]`
- **Find by Class**: `android.widget.ImageView`

### Example Element Properties:
```
Like Button:
- resource-id: "com.zhiliaoapp.musically:id/a9s"
- content-desc: "Like video"
- bounds: [994, 1136, 1080, 1224]
- center: (1037, 1180)
- clickable: true

Video Duration (if visible):
- class: "android.widget.TextView"
- text: "0:23"
- bounds: [980, 2200, 1080, 2250]
```

## 🐍 Python Script Using Appium:

```python
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import time

# Setup
caps = {
    "platformName": "Android",
    "appium:deviceName": "Samsung S20",
    "appium:automationName": "UiAutomator2",
    "appium:appPackage": "com.zhiliaoapp.musically",
    "appium:appActivity": ".MainActivity",
    "appium:noReset": True
}

driver = webdriver.Remote("http://localhost:4723", caps)

# Find elements
def find_like_button():
    try:
        # Try multiple methods
        # Method 1: By content description
        like = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Like")
        
        # Method 2: By resource ID
        # like = driver.find_element(AppiumBy.ID, "com.zhiliaoapp.musically:id/like_button")
        
        # Method 3: By XPath
        # like = driver.find_element(AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='Like']")
        
        # Get location
        location = like.location
        size = like.size
        
        center_x = location['x'] + size['width'] // 2
        center_y = location['y'] + size['height'] // 2
        
        print(f"Like button found at: ({center_x}, {center_y})")
        return like
    except Exception as e:
        print(f"Like button not found: {e}")
        return None

def find_video_duration():
    try:
        # Look for time text
        elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
        
        for elem in elements:
            text = elem.text
            if ':' in text and any(c.isdigit() for c in text):
                print(f"Duration found: {text}")
                return text
                
    except Exception as e:
        print(f"Duration not found: {e}")
    
    return None

# Use the functions
like_btn = find_like_button()
if like_btn:
    like_btn.click()

duration = find_video_duration()
if duration:
    print(f"Video duration: {duration}")

driver.quit()
```

## ⚡ Lightweight Alternative: scrcpy + Coordinates

If Appium seems too heavy, use **scrcpy**:

### Install scrcpy:
```bash
# Windows (with Chocolatey)
choco install scrcpy

# Or download from: https://github.com/Genymobile/scrcpy/releases
```

### Use scrcpy to see coordinates:
1. Run: `scrcpy --show-touches`
2. Touch TikTok buttons
3. See coordinates on screen
4. Note them down

## 🆚 Comparison:

| Tool | Setup Time | Features | Best For |
|------|------------|----------|----------|
| **Appium Inspector** | 30 min | Full element tree, IDs, XPath | Professional automation |
| **scrcpy** | 5 min | Visual only, manual coords | Quick testing |
| **UIAutomator** | 0 min | XML dump | When phone is idle |
| **Manual Testing** | 0 min | Simple | Finding coordinates |

## 💡 Recommendation:

1. **Quick solution**: Use our existing scripts with your coordinates (994, 1136)
2. **Professional**: Setup Appium Inspector (30 minutes)
3. **Visual**: Use scrcpy (5 minutes)

## 🎯 For TikTok specifically:

Appium Inspector will show you:
- Exact like button ID
- Comment button coordinates
- Share button location
- Video duration (if visible)
- All swipe areas
- Hidden elements

Want me to help you set up Appium or continue with the coordinates you already have?