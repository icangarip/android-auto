#!/usr/bin/env python3
"""
TikTok Automation - Locator Version
Requires an Appium server.
"""

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import re
import random
import os
import json
from datetime import datetime

class TikTokWithLocator:
    def __init__(self):
        self.driver = None
        self.wait = None
        
        # Appium server URL
        import os
        self.appium_server = os.getenv('APPIUM_SERVER', 'http://localhost:4723')
        # TikTok package can vary by region (musically/trill)
        self.pkg_candidates = [
            os.getenv('TIKTOK_PACKAGE', 'com.zhiliaoapp.musically'),
            'com.ss.android.ugc.trill'
        ]
        # Fast mode toggle
        self.fast_mode = os.getenv('FAST_MODE', '0') == '1'
        
        # Session & logging
        self.session_folder = None
        self.logs_path = None
        self.screens_dir = None
        self.stats = {"videos": 0, "likes": 0}
        self.liked_videos = []
        
    def connect(self):
        """Connect to Appium server"""
        try:
            print("📱 Connecting to Appium...")
            
            # Appium options
            options = UiAutomator2Options()
            options.platform_name = 'Android'
            options.device_name = 'Samsung S20'
            # Do not auto-launch an activity; attach session and activate explicitly
            options.no_reset = True
            options.auto_grant_permissions = True
            # Prevent Appium from auto-starting an activity
            options.set_capability('appium:autoLaunch', False)
            # Keep session alive during run
            options.set_capability('appium:newCommandTimeout', 120)
            
            self.driver = webdriver.Remote(self.appium_server, options=options)
            # Disable implicit wait for speed
            self.driver.implicitly_wait(0)
            # Short explicit wait
            self.wait = WebDriverWait(self.driver, 3 if self.fast_mode else 5)
            # Reduce UI idle waits (performance)
            try:
                self.driver.update_settings({
                    "ignoreUnimportantViews": True,
                    "waitForIdleTimeout": 0,
                    "waitForIdlePollingInterval": 50
                })
            except Exception:
                pass
            print("✅ Connected to Appium!")
            return True
            
        except Exception as e:
            print(f"❌ Appium connection failed: {e}")
            print("\n⚠️  Ensure Appium server is running:")
            print("   In terminal: appium")
            return False
    
    def open_tiktok(self):
        """Open TikTok or bring to foreground"""
        try:
            current = self.driver.current_package or ''
            if ('musically' not in current) and ('trill' not in current):
                print("🎵 Launching TikTok...")
                for pkg in self.pkg_candidates:
                    try:
                        self.driver.activate_app(pkg)
                        time.sleep(5)
                        current = self.driver.current_package or ''
                        if pkg in current or ('musically' in current) or ('trill' in current):
                            break
                    except Exception:
                        continue
                if ('musically' not in current) and ('trill' not in current):
                    raise RuntimeError('TikTok package could not be activated')
                print(f"✅ TikTok is open: {current}")
            else:
                print(f"✅ TikTok already open: {current}")
            return True
        except Exception as e:
            print(f"❌ Could not open TikTok: {e}")
            return False

    def like_video_with_locator(self):
        """Like the current video using locators"""
        self.log("❤️  Searching for Like button (locators)...")
        
        def smart_click(el):
            try:
                # Try direct click (some devices work even if clickable=false)
                el.click()
                return True
            except Exception:
                pass
            # Click nearest clickable ancestor
            try:
                ancestor = el.find_element(AppiumBy.XPATH, "./ancestor::*[@clickable='true'][1]")
                ancestor.click()
                return True
            except Exception:
                pass
            # Fallback: coordinate-based click (mobile: clickGesture)
            try:
                loc = el.location; sz = el.size
                cx = loc['x'] + max(1, sz['width']//2)
                cy = loc['y'] + max(1, sz['height']//2)
                self.driver.execute_script('mobile: clickGesture', {"x": cx, "y": cy})
                return True
            except Exception:
                return False

        # STRATEGY 0: Fastest: resource-id (...:id/ema)
        rid_candidates = [
            "com.zhiliaoapp.musically:id/ema",
            "com.ss.android.ugc.trill:id/ema"
        ]
        # First try UiSelector (fast)
        for rid in rid_candidates:
            try:
                ui = f'new UiSelector().resourceId("{rid}")'
                el = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui)
                self.log(f"✅ Bulundu: UiSelector resourceId('{rid}')")
                if smart_click(el):
                    return True
            except Exception:
                continue
        # Then try ID
        for rid in rid_candidates:
            try:
                el = self.driver.find_element(AppiumBy.ID, rid)
                self.log(f"✅ Bulundu: id='{rid}'")
                if smart_click(el):
                    return True
            except Exception:
                continue

        # STRATEGY 1: Content-Description (basic English)
        for desc in ["Like", "Unlike"]:
            try:
                like_btn = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, desc)
                self.log(f"✅ Bulundu: content-desc='{desc}'")
                if smart_click(like_btn):
                    return True
            except Exception:
                continue

        # STRATEGY 2: UiSelector descriptionContains('like')
        for kw in ["like"]:
            try:
                selector = f'new UiSelector().descriptionContains("{kw}")'
                el = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, selector)
                self.log(f"✅ Bulundu: descriptionContains('{kw}')")
                if smart_click(el):
                    return True
            except Exception:
                continue

        # STRATEGY 3: XPath content-desc contains Like/like
        try:
            xpath = "//android.widget.ImageView[contains(@content-desc,'Like') or contains(@content-desc,'like')]"
            like_btn = self.driver.find_element(AppiumBy.XPATH, xpath)
            self.log("✅ Found: XPath (content-desc contains)")
            if smart_click(like_btn):
                return True
        except Exception:
            pass

        # STRATEGY 4: Heuristic on right-side action panel (single pass)
        try:
            size = self.driver.get_window_size()
            W, H = size['width'], size['height']
            right_x = int(W * 0.85)

            # Collect numeric labels (like/comment counters)
            nums = []
            for tv in self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView"):
                text = tv.text or ""
                if re.match(r"^\d+[\.,]?\d*[KkMm]?$", text.strip()):
                    loc = tv.location; sz = tv.size
                    cx = loc['x'] + sz['width']//2
                    cy = loc['y'] + sz['height']//2
                    if cx >= right_x:
                        nums.append((tv, cx, cy))

            # Collect clickable icons on the right side
            icons = []
            for iv in self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.ImageView"):
                try:
                    clickable = iv.get_attribute('clickable') == 'true'
                    if not clickable:
                        continue
                    loc = iv.location; sz = iv.size
                    cx = loc['x'] + sz['width']//2
                    cy = loc['y'] + sz['height']//2
                    if cx >= right_x and (H*0.25) <= cy <= (H*0.9):
                        icons.append((iv, cx, cy))
                except Exception:
                    continue

            # Assume the closest icon above a numeric label is the like button
            if nums and icons:
                icons_sorted = sorted(icons, key=lambda x: x[2])
                for (_, _, ny) in sorted(nums, key=lambda x: x[2]):
                    above = [it for it in icons_sorted if it[2] < ny and (ny - it[2]) < int(H*0.25)]
                    if above:
                        cand = above[-1][0]
                        self.log("✅ Found: right panel heuristic icon")
                        cand.click()
                        return True
        except Exception:
            pass
        
        self.log("❌ Like button not found!")
        return False
    
    def swipe_up(self):
        """Swipe up to next video"""
        try:
            print("⬆️  Swiping to next video...")
            size = self.driver.get_window_size()
            
            start_x = size['width'] // 2
            start_y = size['height'] * 0.8
            end_x = size['width'] // 2
            end_y = size['height'] * 0.2
            
            self.driver.swipe(start_x, start_y, end_x, end_y, duration=300)
            return True
        except Exception as e:
            print(f"❌ Swipe failed: {e}")
            return False
    
    def show_all_locators(self, max_seconds: float = 3.0):
        """Quickly list some locators on screen (time-capped)."""
        self.log("\n🔍 Scanning elements (quick mode)...")
        try:
            start = time.time()
            found = []
            # Elements with content-desc
            try:
                elems = self.driver.find_elements(AppiumBy.XPATH, "//*[@content-desc]")
                for el in elems[:20]:
                    cd = el.get_attribute("content-desc")
                    if cd:
                        found.append({'content_desc': cd, 'resource_id': '', 'class': el.get_attribute('className'), 'clickable': el.get_attribute('clickable') == 'true'})
                    if time.time() - start > max_seconds:
                        break
            except Exception:
                pass
            # Elements with resource-id
            if time.time() - start <= max_seconds:
                try:
                    elems = self.driver.find_elements(AppiumBy.XPATH, "//*[@resource-id]")
                    for el in elems[:20]:
                        rid = el.get_attribute("resourceId")
                        if rid:
                            found.append({'content_desc': '', 'resource_id': rid, 'class': el.get_attribute('className'), 'clickable': el.get_attribute('clickable') == 'true'})
                        if time.time() - start > max_seconds:
                            break
                except Exception:
                    pass

            self.log("\n📋 Important elements (first 10):")
            for e in found[:10]:
                if e['content_desc']:
                    self.log(f"  🔘 content-desc: '{e['content_desc']}' (clickable={e['clickable']})")
                if e['resource_id']:
                    self.log(f"  🔘 resource-id: '{e['resource_id']}' (clickable={e['clickable']})")
            return found
        except Exception as e:
            self.log(f"❌ Element scan failed: {e}")
            return []
    
    def run(self):
        """Ana otomasyon"""
        self.log("\n🚀 TikTok Locator Automation Starting")
        self.log("=" * 40)
        
        # 1. Appium bağlantısı
        if not self.connect():
            return False
        
        # 2. TikTok'u aç
        if not self.open_tiktok():
            self.driver.quit()
            return False
        
        # 3. Elementleri göster (debug için, opsiyonel)
        import os
        if os.getenv('SHOW_LOCATORS', '0') == '1':
            self.show_all_locators()

        # Timed run (default 2 min)
        try:
            run_minutes = float(os.getenv('RUN_MINS', '2'))
        except Exception:
            run_minutes = 2.0
        # Session klasörünü kur
        self.setup_session()
        # Optional: switch account
        self.switch_account_name = os.getenv('SWITCH_ACCOUNT', '').strip()
        if self.switch_account_name:
            self.log(f"👤 Switching account to: {self.switch_account_name}")
            if not self.switch_account(self.switch_account_name):
                self.log("⚠️  Account switch failed; continuing anyway")
            else:
                # After switching and verifying, navigate back to Home feed
                if self.open_home_tab():
                    self.log("🏠 Returned to Home tab")
                    time.sleep(2.0)
                else:
                    self.log("⚠️  Could not navigate to Home tab; continuing")
        self.run_for_minutes(run_minutes)

        self.log("\n✅ Automation finished!")
        self.log(f"📊 Duration: ~{run_minutes:g} min | Videos: {self.stats['videos']} | Likes: {self.stats['likes']}")
        # Write report
        self.write_session_report(run_minutes)
        
        # Temizlik
        self.driver.quit()
        return True

    # ---- Account switching ----
    def open_home_tab(self) -> bool:
        """Tap the Home tab on the bottom bar to return to feed."""
        # Try UiSelector by text
        try:
            el = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("Home")'
            )
            el.click()
            return True
        except Exception:
            pass
        # Try XPath by text
        try:
            el = self.driver.find_element(
                AppiumBy.XPATH,
                '//android.widget.TextView[@text="Home"]'
            )
            el.click()
            return True
        except Exception:
            pass
        # Try accessibility id fallback
        try:
            el = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Home')
            el.click()
            return True
        except Exception:
            return False

    def open_profile_tab(self) -> bool:
        """Tap the profile tab button on the bottom bar."""
        try:
            el = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().resourceId("com.zhiliaoapp.musically:id/lcd")'
            )
            el.click()
            return True
        except Exception:
            pass
        try:
            el = self.driver.find_element(AppiumBy.ID, 'com.zhiliaoapp.musically:id/lcd')
            el.click()
            return True
        except Exception:
            return False

    def switch_account(self, account: str) -> bool:
        """Switch to a given account (e.g., 'certmaster8' or 'ccna.exam')."""
        try:
            if not self.open_profile_tab():
                self.log("❌ Could not open profile tab")
                return False
            time.sleep(1.0)
            # Open account switcher by tapping username area
            opened = False
            for locator in [
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("com.zhiliaoapp.musically:id/ovq")'),
                (AppiumBy.ID, 'com.zhiliaoapp.musically:id/ovq'),
            ]:
                try:
                    el = self.driver.find_element(*locator)
                    el.click()
                    opened = True
                    break
                except Exception:
                    continue
            if not opened:
                self.log("❌ Could not open account switcher")
                return False
            time.sleep(1.0)
            # Select account by text
            selected = False
            for name in [account, f"@{account}"]:
                try:
                    el = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{name}")')
                    el.click()
                    selected = True
                    break
                except Exception:
                    continue
            if not selected:
                # XPath fallback
                try:
                    el = self.driver.find_element(
                        AppiumBy.XPATH,
                        f'//android.widget.TextView[@resource-id="com.zhiliaoapp.musically:id/ke3" and @text="{account}"]'
                    )
                    el.click()
                    selected = True
                except Exception:
                    pass
            if not selected:
                self.log(f"❌ Could not find account entry: {account}")
                return False
            # Wait to settle and verify
            self.log("⏳ Waiting for account switch (15s)...")
            time.sleep(15.0)
            if not self.open_profile_tab():
                self.log("⚠️  Could not open profile tab for verification")
            time.sleep(1.0)
            verified = False
            txt = ''
            for locator in [
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("com.zhiliaoapp.musically:id/oxg")'),
                (AppiumBy.ID, 'com.zhiliaoapp.musically:id/oxg'),
            ]:
                try:
                    el = self.driver.find_element(*locator)
                    txt = (el.text or '').strip()
                    if txt:
                        break
                except Exception:
                    continue
            target_variants = [account, f"@{account}"]
            if txt:
                verified = any(v.lower() == txt.lower() for v in target_variants)
            if verified:
                self.log(f"✅ Account switched to: {account}")
                self.save_screenshot(f"after_switch_{account}.png")
                return True
            else:
                self.log(f"❌ Account switch verification failed (header='{txt}')")
                self.save_screenshot("after_switch_failed.png")
                return False
        except Exception as e:
            self.log(f"❌ switch_account exception: {e}")
            return False

    def run_for_minutes(self, minutes: float = 2.0):
        """Verilen dakika boyunca videoları işle ve karar ver."""
        load_secs = float(os.getenv('LOAD_SECS', '1' if self.fast_mode else '2'))
        end_time = time.time() + int(minutes * 60)
        video_idx = 1
        while time.time() < end_time:
            self.log(f"\n📹 Video #{video_idx}")
            time.sleep(load_secs)
            desc = self.get_video_description_text()
            title = self.get_video_title_text()
            if desc:
                preview = desc.replace("\n", " ")
                self.log(f"📝 Description: {preview[:80]}{'...' if len(preview) > 80 else ''}")
            else:
                self.log("📝 No description found")
            if title:
                tprev = title.replace("\n", " ")
                self.log(f"🏷️ Title: {tprev[:80]}{'...' if len(tprev) > 80 else ''}")
            
            # Target content? (keywords in desc or title)
            matched_desc = self.get_matched_keywords(desc)
            matched_title = self.get_matched_keywords(title)
            matched_keys = list(dict.fromkeys(matched_desc + matched_title))
            is_target = len(matched_keys) > 0
            
            # İzleme süresi seçimi
            try:
                if is_target:
                    t_min = float(os.getenv('TARGET_WATCH_MIN_SECS', '25'))
                    t_max = float(os.getenv('TARGET_WATCH_MAX_SECS', '35'))
                    if t_max < t_min:
                        t_max = t_min
                    watch_total = random.uniform(t_min, t_max)
                else:
                    n_min = float(os.getenv('WATCH_MIN_SECS', '10'))
                    n_max = float(os.getenv('WATCH_MAX_SECS', '25'))
                    if n_max < n_min:
                        n_max = n_min
                    watch_total = random.uniform(n_min, n_max)
            except Exception:
                watch_total = 30.0 if is_target else 15.0

            like_scheduled = False
            like_after = None
            like_reason = None  # 'keywords' | 'random'

            if is_target:
                # Target content: early like with a natural delay
                like_scheduled = True
                like_after = min(watch_total * 0.4, random.uniform(1.0, 2.5))
                like_reason = 'keywords'
            else:
                # Non-target: 30% chance to like mid-to-late
                if random.random() < 0.30:
                    like_scheduled = True
                    like_after = random.uniform(watch_total * 0.5, watch_total * 0.9)
                    like_reason = 'random'

            # Watch and like at the scheduled moment
            if like_scheduled and like_after and like_after > 0:
                time.sleep(like_after)
                if like_reason == 'keywords':
                    reason_msg = "keywords: " + (", ".join(matched_keys[:6]) if matched_keys else "unknown")
                else:
                    reason_msg = "random 30%"
                self.log(f"🎯 Decision: LIKE (reason: {reason_msg})")
                if self.like_video_with_locator():
                    self.stats['likes'] += 1
                    snap_name = f"liked_video_{video_idx:03d}.png"
                    self.save_screenshot(snap_name)
                    self.liked_videos.append({
                        "video": video_idx,
                        "desc": (desc or "")[:200],
                        "title": (title or "")[:200],
                        "screenshot": snap_name,
                        "timestamp": datetime.now().isoformat(),
                        "reason": like_reason or "unknown",
                        "keywords": matched_keys
                    })
                else:
                    self.log("⚠️  Like failed (locator)")
                remaining = max(0.0, watch_total - like_after)
                time.sleep(remaining)
            else:
                self.log("🎯 Decision: skip")
                time.sleep(watch_total)

            if time.time() >= end_time:
                break
            if not self.swipe_up():
                self.log("⚠️  Swipe failed, stopping loop")
                break
            video_idx += 1
            self.stats['videos'] = video_idx
        # Döngü bitti

    def get_video_description_text(self) -> str:
        """Resource-id ile video açıklamasını yakala."""
        # UiSelector ile hızlı dene
        for rid in [
            "com.zhiliaoapp.musically:id/desc",
            "com.ss.android.ugc.trill:id/desc"
        ]:
            try:
                ui = f'new UiSelector().resourceId("{rid}")'
                el = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui)
                txt = (el.text or "").strip()
                if txt:
                    return txt
            except Exception:
                continue
        # ID ile dene
        for rid in [
            "com.zhiliaoapp.musically:id/desc",
            "com.ss.android.ugc.trill:id/desc"
        ]:
            try:
                el = self.driver.find_element(AppiumBy.ID, rid)
                txt = (el.text or "").strip()
                if txt:
                    return txt
            except Exception:
                continue
        # XPath ile kısa deneme
        try:
            el = self.driver.find_element(AppiumBy.XPATH, "//*[@resource-id and contains(@resource-id,'/desc')]")
            return (el.text or "").strip()
        except Exception:
            return ""

    def get_video_title_text(self) -> str:
        """Fetch video title using resource-id."""
        # Try UiSelector first
        for rid in [
            "com.zhiliaoapp.musically:id/title",
        ]:
            try:
                ui = f'new UiSelector().resourceId("{rid}")'
                el = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui)
                txt = (el.text or "").strip()
                if txt:
                    return txt
            except Exception:
                continue
        # Then try ID
        for rid in [
            "com.zhiliaoapp.musically:id/title",
        ]:
            try:
                el = self.driver.find_element(AppiumBy.ID, rid)
                txt = (el.text or "").strip()
                if txt:
                    return txt
            except Exception:
                continue
        # Short XPath attempt
        try:
            el = self.driver.find_element(AppiumBy.XPATH, "//*[@resource-id and contains(@resource-id,'/title')]")
            return (el.text or "").strip()
        except Exception:
            return ""

    def should_like_based_on_desc(self, desc: str) -> bool:
        """Return True if CompTIA-related; else like with 30% chance."""
        if not desc:
            return random.random() < 0.30
        text = desc.lower()
        keywords = [
            'comptia', 'security+', 'network+', 'a+', 'aplus', 'cysa+', 'pentest+', 'linux+', 'cloud+', 'server+', 'project+',
            'sy0-601', 'sy0-701', 'n10-008', '220-1101', '220-1102', 'cs0-002', 'pt0-002',
            'cybersecurity', 'network security', 'ethical hacking', 'incident response', 'vulnerability', 'encryption', 'cryptography',
            'malware', 'phishing', 'osi model', 'subnet', 'subnetting', 'tcp/ip', 'ports', 'protocols',
            'certification', 'exam', 'exam prep', 'practice test', 'bootcamp'
        ]
        if any(k in text for k in keywords):
            return True
        return random.random() < 0.30

    def is_target_desc(self, desc: str) -> bool:
        """Whether the text relates to CompTIA/cybersecurity."""
        if not desc:
            return False
        text = desc.lower()
        keywords = [
            'comptia', 'security+', 'network+', 'a+', 'aplus', 'cysa+', 'pentest+', 'linux+', 'cloud+', 'server+', 'project+',
            'sy0-601', 'sy0-701', 'n10-008', '220-1101', '220-1102', 'cs0-002', 'pt0-002',
            'cybersecurity', 'network security', 'ethical hacking', 'incident response', 'vulnerability', 'encryption', 'cryptography',
            'malware', 'phishing', 'osi model', 'subnet', 'subnetting', 'tcp/ip', 'ports', 'protocols',
            'certification', 'exam', 'exam prep', 'practice test', 'bootcamp'
        ]
        return any(k in text for k in keywords)

    def get_matched_keywords(self, desc: str):
        if not desc:
            return []
        text = desc.lower()
        keywords = [
            'comptia', 'security+', 'network+', 'a+', 'aplus', 'cysa+', 'pentest+', 'linux+', 'cloud+', 'server+', 'project+',
            'sy0-601', 'sy0-701', 'n10-008', '220-1101', '220-1102', 'cs0-002', 'pt0-002',
            'cybersecurity', 'network security', 'ethical hacking', 'incident response', 'vulnerability', 'encryption', 'cryptography',
            'malware', 'phishing', 'osi model', 'subnet', 'subnetting', 'tcp/ip', 'ports', 'protocols',
            'certification', 'exam', 'exam prep', 'practice test', 'bootcamp'
        ]
        return [k for k in keywords if k in text]

    # --- Session helpers ---
    def setup_session(self):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_folder = os.path.join('sessions', f'locator_{ts}')
        self.screens_dir = os.path.join(self.session_folder, 'screenshots')
        logs_dir = os.path.join(self.session_folder, 'logs')
        os.makedirs(self.screens_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)
        self.logs_path = os.path.join(logs_dir, 'session.log')
        # Header
        header = f"Session started {ts}\nSession folder: {self.session_folder}\n"
        with open(self.logs_path, 'a', encoding='utf-8') as f:
            f.write(header)
        self.log("📁 Session klasörü hazır")

    def log(self, message: str):
        # Print and append to file
        print(message)
        if self.logs_path:
            try:
                with open(self.logs_path, 'a', encoding='utf-8') as f:
                    f.write(message + "\n")
            except Exception:
                pass

    def save_screenshot(self, filename: str):
        if not self.screens_dir:
            return
        path = os.path.join(self.screens_dir, filename)
        try:
            ok = self.driver.get_screenshot_as_file(path)
            if ok:
                self.log(f"📸 Screenshot kaydedildi: {path}")
        except Exception as e:
            self.log(f"❌ Screenshot başarısız: {e}")

    def write_session_report(self, run_minutes: float):
        if not self.session_folder:
            return
        data = {
            "run_minutes": run_minutes,
            "videos_processed": self.stats.get('videos', 0),
            "likes": self.stats.get('likes', 0),
            "liked_videos": self.liked_videos,
            "timestamp": datetime.now().isoformat()
        }
        try:
            with open(os.path.join(self.session_folder, 'session_report.json'), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.log("💾 Rapor kaydedildi: session_report.json")
        except Exception as e:
            self.log(f"❌ Rapor yazılamadı: {e}")

def main():
    print("🤖 TikTok Locator Automation")
    print("=" * 40)
    print("⚠️  NOTE: This script requires an Appium server!")
    print("\nStart Appium in a terminal:")
    print("   appium")
    print("\nThen run this script.")
    print()
    
    # Appium check (APPIUM_SERVER env)
    import os
    import socket
    from urllib.parse import urlparse

    server_url = os.getenv('APPIUM_SERVER', 'http://localhost:4723')
    parsed = urlparse(server_url)
    host = parsed.hostname or 'localhost'
    port = parsed.port or 4723

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()

    if result != 0:
        print("❌ Cannot connect to Appium server!")
        print(f"   Check: {host}:{port} (APPIUM_SERVER)")
        print("   On Windows: appium -a 0.0.0.0 -p 4723")
        sys.exit(1)

    print(f"✅ Appium server detected: {host}:{port}")
    print("📌 Starting automation...\n")
    
    automation = TikTokWithLocator()
    success = automation.run()
    
    if not success:
        print("\n⚠️  Automation did not complete!")
        sys.exit(1)

if __name__ == "__main__":
    main()
