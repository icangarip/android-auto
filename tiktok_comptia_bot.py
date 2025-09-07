#!/usr/bin/env python3
"""
TikTok CompTIA Bot - Akıllı Otomasyon Sistemi
CompTIA sertifikasyon içeriklerini tespit edip daha fazla etkileşim sağlar
Doğal kullanıcı davranışı simülasyonu ile bot tespitinden kaçınır
"""

import subprocess
import time
import random
import re
import xml.etree.ElementTree as ET
import os
import json
import math
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class CompTIATikTokBot:
    def __init__(self):
        # ADB Path
        self.adb_path = "/mnt/c/Users/canga/Desktop/platform-tools/adb.exe"
        
        # Ekran boyutları
        self.screen_width = 1080
        self.screen_height = 2400
        
        # Real user interaction coordinates (from actual usage data)
        self.ui_elements = {
            'like_button': (989, 1176),      # Gerçek kalp butonu merkezi
            'like_button_alt': (942, 1285),  # Alternatif like koordinatı
            'comment_button': (972, 1363),   # Gerçek yorum butonu
            'comment_button_alt': (983, 1464), # Alternatif yorum koordinatı
            'comment_back': (827, 662),      # Yorum kapama butonu
            'comment_back_alt': (592, 715),  # Alternatif yorum kapama
            'profile_avatar': (989, 1085),   # Profil resmi (unchanged)
            'follow_button': (989, 1151),    # Takip butonu (unchanged)
            'save_button': (989, 1540),      # Save/bookmark button
        }
        
        # Double tap like areas (real user data)
        self.double_tap_areas = [
            (698, 1299),   # Gerçek çift tıklama 1
            (732, 1643),   # Gerçek çift tıklama 2  
            (771, 1539),   # Gerçek çift tıklama 3
        ]
        
        # Real user swipe patterns (analyzed from actual usage)
        # Format: (x1, y1, x2, y2) where x1<x2 and y1<y2 ALWAYS
        self.real_swipe_patterns = [
            # Pattern 1: Start lower right, end middle-upper with right bias
            {'start_area': (750, 1750, 900, 1850), 'end_area': (950, 1350, 1050, 1450)},
            
            # Pattern 2: Start middle-right, end middle-upper  
            {'start_area': (750, 1650, 850, 1750), 'end_area': (850, 1300, 950, 1400)},
            
            # Pattern 3: Start right, end upper-right
            {'start_area': (800, 1650, 950, 1750), 'end_area': (1000, 1300, 1100, 1450)},
            
            # Pattern 4: Longer swipe - lower to upper (FIXED)
            {'start_area': (650, 1650, 750, 1750), 'end_area': (1000, 950, 1100, 1050)},
            
            # Pattern 5: Standard middle swipe with right drift
            {'start_area': (850, 1600, 950, 1700), 'end_area': (950, 1250, 1050, 1350)},
        ]
        
        # CompTIA anahtar kelimeleri (geniş liste)
        self.comptia_keywords = [
            # Sertifikalar
            'comptia', 'security+', 'network+', 'a+', 'aplus', 'cysa+', 
            'pentest+', 'linux+', 'cloud+', 'server+', 'project+',
            # İlgili terimler
            'certification', 'cert', 'exam', 'sy0-601', 'sy0-701', 'n10-008',
            '220-1101', '220-1102', 'cs0-002', 'pt0-002', 
            # Konu başlıkları
            'cybersecurity', 'cyber security', 'network security', 'ethical hacking',
            'penetration testing', 'incident response', 'vulnerability', 
            'firewall', 'encryption', 'cryptography', 'malware', 'phishing',
            'ports', 'protocols', 'tcp/ip', 'osi model', 'subnetting',
            'troubleshooting', 'hardware', 'software', 'operating system',
            # Eğitim
            'study', 'tips', 'passed', 'failed', 'exam prep', 'practice test',
            'bootcamp', 'course', 'tutorial', 'learn', 'it career'
        ]
        
        # Davranış parametreleri
        self.behavior_params = {
            'comptia_video': {
                'watch_time': (15, 45),      # Daha uzun izleme
                'like_chance': 0.75,         # %75 beğeni şansı
                'comment_chance': 0.10,      # %10 yorum açma
                'save_chance': 0.30,         # %30 kaydetme
                'profile_visit_chance': 0.15, # %15 profil ziyareti
            },
            'normal_video': {
                'watch_time': (3, 20),       # Normal izleme
                'like_chance': 0.20,         # %20 beğeni şansı
                'comment_chance': 0.02,      # %2 yorum açma
                'save_chance': 0.05,         # %5 kaydetme
                'profile_visit_chance': 0.03, # %3 profil ziyareti
            }
        }
        
        # İstatistikler
        self.stats = {
            'videos_watched': 0,
            'comptia_videos': 0,
            'likes_given': 0,
            'comments_opened': 0,
            'videos_saved': 0,
            'profiles_visited': 0,
            'total_watch_time': 0
        }
        
        # Doğal davranış için değişkenler
        self.last_action_time = time.time()
        self.session_start = None
        self.energy_level = 1.0  # Başlangıçta enerjik, zamanla azalır
        
        # Session klasörü ve logging
        self.session_folder = None
        self.log_file = None
        self.session_logs = []
        
        # Advanced human behavior simulation
        self.user_profile = {
            'dominant_hand': random.choice(['right', 'left']),  # Dominant el
            'finger_size': random.uniform(0.8, 1.2),          # Parmak boyutu faktörü
            'precision_level': random.uniform(0.7, 1.3),      # Hassasiyet seviyesi
            'swipe_style': random.choice(['curved', 'straight', 'lazy']),  # Swipe tarzı
            'speed_preference': random.uniform(0.6, 1.4),     # Hız tercihi
        }
        
        # Learning and adaptation
        self.touch_history = []  # Son tıklama konumları
        self.swipe_patterns = []  # Son swipe patternleri
        self.interaction_count = 0  # Etkileşim sayısı

    def setup_session_folder(self):
        """Session için klasör oluştur ve log dosyası başlat"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_folder = f"sessions/comptia_bot_{timestamp}"
        
        # Klasörleri oluştur
        os.makedirs(self.session_folder, exist_ok=True)
        os.makedirs(f"{self.session_folder}/screenshots", exist_ok=True)
        os.makedirs(f"{self.session_folder}/logs", exist_ok=True)
        
        # Log dosyası başlat
        self.log_file = f"{self.session_folder}/logs/session.log"
        
        self.log(f"🚀 Session started: {timestamp}")
        self.log(f"📁 Folder: {self.session_folder}")
        
        # Log user profile for analysis
        self.log(f"👤 User Profile:")
        self.log(f"   • Dominant hand: {self.user_profile['dominant_hand']}")
        self.log(f"   • Finger size factor: {self.user_profile['finger_size']:.2f}")
        self.log(f"   • Precision level: {self.user_profile['precision_level']:.2f}")
        self.log(f"   • Swipe style: {self.user_profile['swipe_style']}")
        self.log(f"   • Speed preference: {self.user_profile['speed_preference']:.2f}")

    def log(self, message: str):
        """Log mesajı yaz (hem dosyaya hem konsola)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Konsola yaz
        print(log_entry)
        
        # Log listesine ekle
        self.session_logs.append({
            'timestamp': timestamp,
            'message': message,
            'full_timestamp': datetime.now().isoformat()
        })
        
        # Dosyaya yaz
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
            except:
                pass

    def run_adb(self, command: List[str]) -> Optional[str]:
        """ADB komutu çalıştır ve çıktıyı döndür"""
        full_command = [self.adb_path] + command
        try:
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return result.stdout
            return None
        except:
            return None

    def take_screenshot(self, filename: str) -> bool:
        """Screenshot al ve session klasörüne kaydet"""
        if not self.session_folder:
            return False
        
        # Telefonda screenshot al
        screenshot_path = f"/sdcard/temp_screenshot.png"
        if not self.run_adb(['shell', 'screencap', '-p', screenshot_path]):
            return False
        
        time.sleep(0.5)
        
        # PC'ye çek
        local_path = f"{self.session_folder}/screenshots/{filename}"
        if not self.run_adb(['pull', screenshot_path, local_path]):
            return False
        
        # Telefondaki temp dosyayı sil
        self.run_adb(['shell', 'rm', screenshot_path])
        
        self.log(f"📸 Screenshot kaydedildi: {filename}")
        return True

    def tap(self, x: int, y: int, pressure: str = "normal") -> bool:
        """Advanced human-like tap simulation with learning and adaptation"""
        self.interaction_count += 1
        
        # Base variance based on pressure and user profile
        base_variance = {
            "light": 8,
            "normal": 15, 
            "heavy": 25
        }.get(pressure, 15)
        
        # Adjust variance based on user characteristics
        variance = base_variance * self.user_profile['finger_size'] / self.user_profile['precision_level']
        
        # Energy level affects precision (tiredness = less precision)
        fatigue_factor = 2 - self.energy_level  # 1.0 to 1.5
        variance *= fatigue_factor
        
        # Dominant hand bias
        hand_bias_x = 3 if self.user_profile['dominant_hand'] == 'right' else -3
        hand_bias_y = random.uniform(-2, 2)
        
        # Learning effect - if we've tapped near this area before, we get better
        learning_adjustment_x = 0
        learning_adjustment_y = 0
        
        if self.touch_history:
            # Find similar recent taps
            similar_taps = [(hx, hy) for hx, hy in self.touch_history[-10:] 
                          if abs(hx - x) < 50 and abs(hy - y) < 50]
            
            if similar_taps:
                # We're getting better at this area - reduce variance slightly
                variance *= 0.85
                # Slight bias towards previous successful taps
                avg_offset_x = sum(hx - x for hx, hy in similar_taps) / len(similar_taps)
                avg_offset_y = sum(hy - y for hx, hy in similar_taps) / len(similar_taps)
                learning_adjustment_x = avg_offset_x * 0.3
                learning_adjustment_y = avg_offset_y * 0.3
        
        # Generate tap coordinates with multiple natural factors
        # Using beta distribution for more realistic off-center bias
        beta_x = random.betavariate(2, 2) - 0.5  # -0.5 to 0.5, center-biased
        beta_y = random.betavariate(2, 2) - 0.5
        
        tap_x = int(x + 
                   (beta_x * variance * 2) +  # Main variance
                   hand_bias_x +              # Dominant hand bias
                   learning_adjustment_x +    # Learning effect
                   random.uniform(-2, 2))     # Small random noise
        
        tap_y = int(y + 
                   (beta_y * variance * 2) +
                   hand_bias_y +
                   learning_adjustment_y +
                   random.uniform(-2, 2))
        
        # Screen boundaries with natural margin
        margin = 15
        tap_x = max(margin, min(tap_x, self.screen_width - margin))
        tap_y = max(100, min(tap_y, self.screen_height - margin))
        
        # Store this tap for learning
        self.touch_history.append((tap_x, tap_y))
        if len(self.touch_history) > 20:  # Keep only recent history
            self.touch_history.pop(0)
        
        # Simulate pressure variation with touch duration
        press_duration = 50 if pressure == "light" else (120 if pressure == "heavy" else 80)
        press_duration = int(press_duration * self.user_profile['speed_preference'])
        
        # Use simple tap for now (motionevent might not be supported)
        return self.run_adb(['shell', 'input', 'tap', str(tap_x), str(tap_y)]) is not None

    def double_tap_like(self) -> bool:
        """Real user double-tap like based on actual usage data"""
        # Choose from real user double-tap locations
        base_location = random.choice(self.double_tap_areas)
        base_x, base_y = base_location
        
        # Add natural variance around the real location
        variance_x = int(40 * self.user_profile['finger_size'] / self.user_profile['precision_level'])
        variance_y = int(30 * self.user_profile['finger_size'] / self.user_profile['precision_level'])
        
        # First tap location
        tap1_x = base_x + random.randint(-variance_x, variance_x)
        tap1_y = base_y + random.randint(-variance_y, variance_y)
        
        # First tap with light pressure
        if not self.tap(tap1_x, tap1_y, "light"):
            return False
        
        # Real user double-tap timing analysis: 80-180ms between taps
        base_interval = random.uniform(0.08, 0.18)
        
        # Speed preference affects interval
        speed_factor = self.user_profile['speed_preference']
        interval = base_interval / speed_factor
        
        # Energy affects reaction time
        energy_penalty = (2 - self.energy_level) * 0.03
        interval += energy_penalty
        
        # Natural jitter
        interval += random.uniform(-0.02, 0.02)
        interval = max(0.06, min(interval, 0.25))
        
        time.sleep(interval)
        
        # Second tap - real users have consistent drift patterns
        # Analyze the real data: drift is usually 10-25px in various directions
        drift_patterns = [
            (-15, -10), (-8, -18), (12, -15), (5, -22),  # Up-ward drifts
            (-12, 8), (15, 10), (-20, 15), (18, 5),      # Down-ward drifts
            (0, 0), (-3, 2), (4, -1)                     # Minimal drifts
        ]
        
        drift_x, drift_y = random.choice(drift_patterns)
        
        # Apply fatigue factor to drift
        fatigue_multiplier = (2 - self.energy_level)
        drift_x = int(drift_x * fatigue_multiplier)
        drift_y = int(drift_y * fatigue_multiplier)
        
        tap2_x = tap1_x + drift_x
        tap2_y = tap1_y + drift_y
        
        # Keep within reasonable bounds
        tap2_x = max(100, min(tap2_x, self.screen_width - 100))
        tap2_y = max(200, min(tap2_y, self.screen_height - 200))
        
        # Second tap with normal pressure
        return self.tap(tap2_x, tap2_y, "normal")

    def button_like(self) -> bool:
        """Real user like button tapping with coordinate variation"""
        # Choose between main and alternative like button coordinates
        if random.random() < 0.7:
            like_x, like_y = self.ui_elements['like_button']      # Primary: (989, 1176)
        else:
            like_x, like_y = self.ui_elements['like_button_alt']  # Alternative: (942, 1285)
        
        # Real users don't hit the exact center - add natural variance
        precision_factor = self.user_profile['precision_level']
        size_factor = self.user_profile['finger_size']
        
        # Like buttons have larger tap areas, so more variance is acceptable
        variance_x = int(25 / precision_factor * size_factor)
        variance_y = int(20 / precision_factor * size_factor)
        
        # Energy affects button targeting precision
        energy_variance = int((2 - self.energy_level) * 15)
        variance_x += energy_variance
        variance_y += energy_variance
        
        # Apply the variance
        final_x = like_x + random.randint(-variance_x, variance_x)
        final_y = like_y + random.randint(-variance_y, variance_y)
        
        # Ensure we stay within reasonable button area
        final_x = max(like_x - 40, min(final_x, like_x + 40))
        final_y = max(like_y - 35, min(final_y, like_y + 35))
        
        return self.tap(final_x, final_y, "normal")

    def generate_natural_swipe_path(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """Generate natural human-like swipe path with micro-movements"""
        path = []
        
        # Number of points based on distance and user style
        distance = ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
        num_points = max(5, int(distance / 30))  # More points for longer swipes
        
        # User style affects curve intensity
        style_factor = {
            'straight': 0.1,
            'curved': 0.3,
            'lazy': 0.5
        }.get(self.user_profile['swipe_style'], 0.3)
        
        for i in range(num_points):
            progress = i / (num_points - 1)
            
            # Linear interpolation
            base_x = start_x + (end_x - start_x) * progress
            base_y = start_y + (end_y - start_y) * progress
            
            # Add natural curve (sine wave)
            curve_intensity = style_factor * self.energy_level * 20
            curve_offset_x = curve_intensity * math.sin(progress * math.pi) * random.uniform(0.5, 1.5)
            curve_offset_y = curve_intensity * 0.3 * math.sin(progress * math.pi * 2)
            
            # Add micro-tremor (natural hand shake)
            tremor_x = random.uniform(-2, 2) * (1.5 - self.energy_level)  # More tremor when tired
            tremor_y = random.uniform(-2, 2) * (1.5 - self.energy_level)
            
            # Dominant hand bias affects curve direction
            hand_bias = 1 if self.user_profile['dominant_hand'] == 'right' else -1
            curve_offset_x *= hand_bias
            
            # Speed variation affects precision
            speed_factor = self.user_profile['speed_preference']
            if speed_factor > 1.1:  # Fast swiper = less precision
                tremor_x *= 1.5
                tremor_y *= 1.5
            
            final_x = int(base_x + curve_offset_x + tremor_x)
            final_y = int(base_y + curve_offset_y + tremor_y)
            
            # Keep within screen bounds
            final_x = max(20, min(final_x, self.screen_width - 20))
            final_y = max(100, min(final_y, self.screen_height - 100))
            
            path.append((final_x, final_y))
        
        return path

    def swipe_next_video(self) -> bool:
        """Simple, reliable swipe with natural variation"""
        self.interaction_count += 1
        
        # Simple, working swipe coordinates (bottom to top)
        # Start area: lower part of screen with some randomness
        start_x = random.randint(400, 700)  # Center-left to center-right
        start_y = random.randint(1600, 1800)  # Lower part
        
        # End area: upper part of screen
        end_x = random.randint(400, 700)   # Similar horizontal range
        end_y = random.randint(800, 1000)  # Upper part
        
        # Natural duration variation
        duration = random.randint(300, 500)
        
        self.log(f"🔄 Swiping from ({start_x},{start_y}) to ({end_x},{end_y}) in {duration}ms")
        
        # Get current video info before swipe for validation
        video_info_before = self.get_video_description()
        
        # Execute the swipe
        success = self.execute_simple_swipe(start_x, start_y, end_x, end_y, duration)
        
        if success:
            # Wait for video to load
            time.sleep(1.0)
            
            # Check if video actually changed
            video_changed = self.validate_video_change(video_info_before)
            
            if video_changed:
                self.log("✅ Video changed successfully")
                return True
            else:
                self.log("⚠️ Video did not change - trying again")
                # Try a different swipe
                start_x = random.randint(500, 600)
                start_y = random.randint(1700, 1900)
                end_x = random.randint(500, 600)
                end_y = random.randint(700, 900)
                duration = random.randint(400, 600)
                
                success = self.execute_simple_swipe(start_x, start_y, end_x, end_y, duration)
                if success:
                    time.sleep(1.0)
                    return self.validate_video_change(video_info_before)
        
        return success
    
    def validate_video_change(self, previous_video_info: Dict[str, str]) -> bool:
        """Check if video actually changed by comparing UI elements"""
        try:
            # Get current video info
            current_video_info = self.get_video_description()
            
            # Compare key indicators
            desc_changed = current_video_info.get('description', '') != previous_video_info.get('description', '')
            user_changed = current_video_info.get('username', '') != previous_video_info.get('username', '')
            likes_changed = current_video_info.get('likes', '') != previous_video_info.get('likes', '')
            
            # Video changed if any of these are different
            changed = desc_changed or user_changed or likes_changed
            
            if changed:
                self.log(f"📹 Video change detected:")
                if desc_changed:
                    self.log(f"   📝 Description: '{previous_video_info.get('description', '')[:30]}...' -> '{current_video_info.get('description', '')[:30]}...'")
                if user_changed:
                    self.log(f"   👤 User: '{previous_video_info.get('username', '')}' -> '{current_video_info.get('username', '')}'")
                if likes_changed:
                    self.log(f"   ❤️ Likes: '{previous_video_info.get('likes', '')}' -> '{current_video_info.get('likes', '')}'")
            else:
                self.log("⚠️ No video change detected - same content")
                
            return changed
            
        except Exception as e:
            self.log(f"Video validation error: {e}")
            # If we can't validate, assume it worked
            return True
    
    def execute_simple_swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int) -> bool:
        """Execute simple swipe command that actually works"""
        try:
            # Use basic input swipe command - this works on all Android devices
            success = self.run_adb([
                'shell', 'input', 'swipe', 
                str(start_x), str(start_y),
                str(end_x), str(end_y),
                str(duration_ms)
            ])
            
            if success:
                self.log(f"✅ Swipe executed: ({start_x},{start_y}) -> ({end_x},{end_y}) in {duration_ms}ms")
            else:
                self.log(f"❌ Swipe failed: ({start_x},{start_y}) -> ({end_x},{end_y})")
                
            return success
            
        except Exception as e:
            self.log(f"Swipe execution error: {e}")
            return False

    def get_video_description(self) -> Dict[str, str]:
        """UIAutomator ile video açıklamasını al"""
        # UI dump al
        self.run_adb(['shell', 'uiautomator', 'dump', '/sdcard/ui_dump.xml'])
        time.sleep(0.3)
        
        # XML'i oku
        xml_content = self.run_adb(['shell', 'cat', '/sdcard/ui_dump.xml'])
        
        if not xml_content:
            return {'description': '', 'username': '', 'likes': ''}
        
        video_info = {
            'description': '',
            'username': '',
            'likes': '',
            'music': ''
        }
        
        try:
            root = ET.fromstring(xml_content)
            
            # Collect all text elements for more robust parsing
            all_texts = []
            for elem in root.iter('node'):
                resource_id = elem.get('resource-id', '')
                text = elem.get('text', '')
                content_desc = elem.get('content-desc', '')
                class_name = elem.get('class', '')
                
                if text and len(text.strip()) > 0:
                    all_texts.append({
                        'text': text,
                        'resource_id': resource_id,
                        'content_desc': content_desc,
                        'class': class_name
                    })
            
            # Enhanced parsing logic
            for item in all_texts:
                text = item['text']
                resource_id = item['resource_id']
                content_desc = item['content_desc']
                
                # Look for username patterns (starts with @)
                if text.startswith('@') and not video_info['username']:
                    video_info['username'] = text
                
                # Look for like count patterns (numbers with K, M, or just digits)
                elif re.match(r'^\d+[KMB]?$', text.replace(',', '')) and not video_info['likes']:
                    video_info['likes'] = text
                
                # Look for description text (longer text without @ or numbers)
                elif len(text) > 10 and not text.startswith('@') and not re.match(r'^\d+[KMB]?$', text.replace(',', '')) and not video_info['description']:
                    video_info['description'] = text.lower()
                
                # Music info from content descriptions
                if 'sound' in content_desc.lower() or 'music' in content_desc.lower():
                    video_info['music'] = content_desc
                    
        except:
            pass
        
        # Temizlik
        self.run_adb(['shell', 'rm', '/sdcard/ui_dump.xml'])
        
        return video_info

    def is_comptia_content(self, video_info: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Video CompTIA içeriği mi kontrol et"""
        found_keywords = []
        
        # Açıklama ve kullanıcı adında ara
        search_text = f"{video_info.get('description', '')} {video_info.get('username', '')}"
        search_text = search_text.lower()
        
        for keyword in self.comptia_keywords:
            if keyword.lower() in search_text:
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords

    def save_video_info(self, screenshot_name: str, video_info: Dict, is_comptia: bool, keywords: List[str], like_method: str):
        """Beğenilen video bilgilerini JSON olarak kaydet"""
        if not self.session_folder:
            return
        
        video_data = {
            'screenshot': screenshot_name,
            'timestamp': datetime.now().isoformat(),
            'video_number': self.stats['videos_watched'],
            'is_comptia': is_comptia,
            'found_keywords': keywords,
            'like_method': like_method,
            'video_info': {
                'username': video_info.get('username', ''),
                'description': video_info.get('description', ''),
                'likes': video_info.get('likes', ''),
                'music': video_info.get('music', '')
            }
        }
        
        # JSON dosyasına kaydet
        json_file = f"{self.session_folder}/logs/liked_videos.json"
        
        try:
            # Mevcut dosyayı oku
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'liked_videos': []}
            
            # Yeni videoyu ekle
            data['liked_videos'].append(video_data)
            
            # Dosyaya yaz
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.log(f"📄 Video bilgileri kaydedildi: {len(data['liked_videos'])} total")
            
        except Exception as e:
            self.log(f"❌ JSON kaydetme hatası: {e}")

    def natural_wait(self, min_sec: float = 0.5, max_sec: float = 2.0):
        """Advanced natural waiting with human-like patterns"""
        # Base wait time
        base_wait = random.uniform(min_sec, max_sec)
        
        # User speed preference affects wait times
        speed_adjusted_wait = base_wait / self.user_profile['speed_preference']
        
        # Fatigue factor increases wait times
        fatigue_factor = 1.0 + (1.0 - self.energy_level) * 0.6
        
        # Interaction count affects wait - users get faster with practice
        practice_factor = max(0.7, 1.0 - (self.interaction_count * 0.005))
        
        # Random micro-pauses (like real users who sometimes hesitate)
        micro_pause_chance = 0.15 * (2 - self.energy_level)  # More likely when tired
        
        actual_wait = speed_adjusted_wait * fatigue_factor * practice_factor
        
        # Sometimes add a micro pause
        if random.random() < micro_pause_chance:
            micro_pause = random.uniform(0.3, 1.2)
            actual_wait += micro_pause
        
        # Natural bounds
        actual_wait = max(0.1, min(actual_wait, max_sec * 3))
        
        time.sleep(actual_wait)

    def simulate_human_behavior(self):
        """İnsan benzeri rastgele davranışlar"""
        behavior_chance = random.random()
        
        if behavior_chance < 0.05:  # %5 - Telefonu kontrol etme
            self.log("   📱 Kısa mola...")
            time.sleep(random.uniform(2, 5))
            
        elif behavior_chance < 0.10:  # %5 - Yanlışlıkla swipe
            self.log("   ↔️ Yanlış swipe, geri dönüş...")
            # Ters swipe
            # Use screen center area for random swipe behavior
            zone = (540, 1200, 150)  # (x, y, radius)
            self.run_adb(['shell', 'input', 'swipe',
                         str(zone['end'][0]), str(zone['end'][1]),
                         str(zone['start'][0]), str(zone['start'][1]),
                         '300'])
            time.sleep(1)
            # Tekrar doğru swipe
            self.swipe_next_video()

    def watch_video(self, is_comptia: bool, keywords: List[str], video_info: Dict[str, str]) -> Dict[str, bool]:
        """Video izleme ve etkileşim"""
        actions = {
            'liked': False,
            'saved': False,
            'commented': False,
            'profile_visited': False
        }
        
        # CompTIA içeriği ise parametreleri ayarla
        if is_comptia:
            params = self.behavior_params['comptia_video']
            self.log(f"   🎯 CompTIA içeriği bulundu! Keywords: {', '.join(keywords[:3])}")
        else:
            params = self.behavior_params['normal_video']
        
        # İzleme süresi hesapla
        watch_time = random.uniform(*params['watch_time'])
        
        # Enerji seviyesine göre ayarla
        watch_time *= self.energy_level
        
        self.log(f"   ⏱️ {watch_time:.1f} saniye izlenecek...")
        
        # Video izlerken ara ara etkileşimler
        start_watch = time.time()
        
        while time.time() - start_watch < watch_time:
            elapsed = time.time() - start_watch
            remaining = watch_time - elapsed
            
            # Beğeni (videonun %30-70'i arasında)
            if not actions['liked'] and elapsed > watch_time * 0.3 and random.random() < params['like_chance']:
                # %60 çift tıklama, %40 buton
                like_method = "double_tap" if random.random() < 0.6 else "button"
                
                if like_method == "double_tap":
                    self.log("   ❤️ Çift tıklama beğeni")
                    self.double_tap_like()
                else:
                    self.log("   ❤️ Buton beğeni")
                    self.button_like()
                
                actions['liked'] = True
                self.stats['likes_given'] += 1
                
                # Screenshot al
                screenshot_name = f"liked_video_{self.stats['videos_watched']:03d}_{like_method}.png"
                self.take_screenshot(screenshot_name)
                
                # Video bilgilerini JSON olarak kaydet
                self.save_video_info(screenshot_name, video_info, is_comptia, keywords, like_method)
                
                self.natural_wait(0.5, 1.5)
            
            # Kaydetme (CompTIA içeriği için)
            if is_comptia and not actions['saved'] and elapsed > watch_time * 0.5 and random.random() < params['save_chance']:
                self.log("   💾 Video kaydediliyor")
                save_x, save_y = self.ui_elements['save_button']
                self.tap(save_x, save_y)
                actions['saved'] = True
                self.stats['videos_saved'] += 1
                self.natural_wait(0.5, 1.0)
            
            # Yorum açma (nadir)
            if not actions['commented'] and elapsed > watch_time * 0.4 and random.random() < params['comment_chance']:
                self.log("   💬 Yorumlar açılıyor")
                comment_x, comment_y = self.ui_elements['comment_button']
                self.tap(comment_x, comment_y)
                actions['commented'] = True
                self.stats['comments_opened'] += 1
                
                # Yorumlarda biraz gezin
                time.sleep(random.uniform(3, 8))
                
                # Geri dön
                self.run_adb(['shell', 'input', 'keyevent', 'KEYCODE_BACK'])
                self.natural_wait(0.5, 1.0)
            
            # Kalan süreyi bekle
            if remaining > 2:
                time.sleep(min(2, remaining))
            else:
                time.sleep(remaining)
                break
        
        # Profil ziyareti (video sonunda)
        if random.random() < params['profile_visit_chance']:
            self.log("   👤 Profile bakılıyor")
            profile_x, profile_y = self.ui_elements['profile_avatar']
            self.tap(profile_x, profile_y)
            actions['profile_visited'] = True
            self.stats['profiles_visited'] += 1
            
            # Profilde biraz gez
            time.sleep(random.uniform(2, 5))
            
            # Geri dön
            self.run_adb(['shell', 'input', 'keyevent', 'KEYCODE_BACK'])
            self.natural_wait(0.5, 1.0)
        
        self.stats['total_watch_time'] += watch_time
        
        return actions

    def run_session(self, duration_minutes: int = 5):
        """Ana otomasyon oturumu"""
        # Session klasörünü hazırla
        self.setup_session_folder()
        
        self.log("🚀 CompTIA TikTok Bot Başlatılıyor")
        self.log("=" * 50)
        self.log(f"⏰ Süre: {duration_minutes} dakika")
        self.log(f"🎯 Hedef: CompTIA içerikleri")
        self.log("=" * 50)
        
        self.session_start = time.time()
        session_end = self.session_start + (duration_minutes * 60)
        
        # TikTok'u aç
        self.log("📱 TikTok açılıyor...")
        self.run_adb(['shell', 'monkey', '-p', 'com.zhiliaoapp.musically',
                     '-c', 'android.intent.category.LAUNCHER', '1'])
        time.sleep(5)
        
        video_count = 0
        
        while time.time() < session_end:
            video_count += 1
            self.stats['videos_watched'] = video_count
            
            # Enerji seviyesi güncelle (yorgunluk simülasyonu)
            elapsed_ratio = (time.time() - self.session_start) / (duration_minutes * 60)
            self.energy_level = max(0.5, 1.0 - (elapsed_ratio * 0.4))
            
            self.log(f"📹 Video #{video_count}")
            self.log(f"   ⚡ Enerji: {self.energy_level*100:.0f}%")
            
            # Video bilgilerini al
            video_info = self.get_video_description()
            
            # CompTIA içeriği mi kontrol et
            is_comptia, keywords = self.is_comptia_content(video_info)
            
            if is_comptia:
                self.stats['comptia_videos'] += 1
            
            # Username varsa göster
            if video_info.get('username'):
                self.log(f"   👤 @{video_info['username']}")
            
            # Videoyu izle ve etkileşim yap
            actions = self.watch_video(is_comptia, keywords, video_info)
            
            # Rastgele insan davranışı
            self.simulate_human_behavior()
            
            # Sonraki videoya geç
            if time.time() < session_end - 5:  # Son 5 saniye swipe yapma
                self.log("   ⬆️ Sonraki video...")
                try:
                    swipe_success = self.swipe_next_video()
                    if not swipe_success:
                        self.log("   ⚠️ Swipe failed, retrying with fallback...")
                        # Fallback swipe
                        self.run_adb(['shell', 'input', 'swipe', '800', '1700', '900', '1300', '400'])
                except Exception as e:
                    self.log(f"   ❌ Swipe error: {e}")
                    # Emergency fallback
                    self.run_adb(['shell', 'input', 'swipe', '800', '1700', '900', '1300', '400'])
                
                self.natural_wait(0.5, 3.0)
        
        # Oturum raporu
        self.print_session_report()

    def save_session_report(self):
        """Session raporunu JSON olarak kaydet"""
        if not self.session_folder:
            return
        
        duration = (time.time() - self.session_start) / 60
        
        session_report = {
            'session_info': {
                'timestamp': datetime.now().isoformat(),
                'duration_minutes': round(duration, 1),
                'folder': self.session_folder
            },
            'user_profile': self.user_profile,
            'interaction_patterns': {
                'total_interactions': self.interaction_count,
                'touch_history_samples': self.touch_history[-5:] if self.touch_history else [],
                'swipe_patterns_samples': self.swipe_patterns[-3:] if self.swipe_patterns else [],
                'final_energy_level': round(self.energy_level, 2)
            },
            'statistics': {
                'videos_watched': self.stats['videos_watched'],
                'comptia_videos': self.stats['comptia_videos'],
                'comptia_percentage': round(self.stats['comptia_videos']/max(1,self.stats['videos_watched'])*100, 1),
                'likes_given': self.stats['likes_given'],
                'videos_saved': self.stats['videos_saved'],
                'comments_opened': self.stats['comments_opened'],
                'profiles_visited': self.stats['profiles_visited'],
                'total_watch_time': round(self.stats['total_watch_time'], 1),
                'average_watch_time': round(self.stats['total_watch_time']/max(1,self.stats['videos_watched']), 1)
            },
            'logs': self.session_logs
        }
        
        # JSON raporunu kaydet
        report_file = f"{self.session_folder}/logs/session_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(session_report, f, indent=2, ensure_ascii=False)
            
            self.log(f"📄 Session raporu kaydedildi: session_report.json")
        except Exception as e:
            self.log(f"❌ Rapor kaydetme hatası: {e}")

    def print_session_report(self):
        """Oturum sonuç raporu"""
        self.log("\n" + "=" * 50)
        self.log("📊 OTURUM RAPORU")
        self.log("=" * 50)
        
        duration = (time.time() - self.session_start) / 60
        
        self.log(f"⏱️ Toplam Süre: {duration:.1f} dakika")
        self.log(f"📹 İzlenen Video: {self.stats['videos_watched']}")
        self.log(f"🎯 CompTIA Video: {self.stats['comptia_videos']} ({self.stats['comptia_videos']/max(1,self.stats['videos_watched'])*100:.0f}%)")
        self.log(f"❤️ Beğeni: {self.stats['likes_given']}")
        self.log(f"💾 Kaydedilen: {self.stats['videos_saved']}")
        self.log(f"💬 Yorum Açılan: {self.stats['comments_opened']}")
        self.log(f"👤 Profil Ziyareti: {self.stats['profiles_visited']}")
        self.log(f"⏰ Ortalama İzleme: {self.stats['total_watch_time']/max(1,self.stats['videos_watched']):.1f} sn/video")
        
        # Başarı mesajı
        if self.stats['comptia_videos'] > 0:
            self.log(f"\n✅ {self.stats['comptia_videos']} CompTIA videosu bulundu ve etkileşim sağlandı!")
        
        self.log(f"\n📁 Session dosyaları: {self.session_folder}")
        self.log(f"📸 Screenshots: {self.stats['likes_given']} adet")
        self.log("\n🎉 Bot başarıyla tamamlandı!")
        
        # JSON raporu kaydet
        self.save_session_report()

def main():
    """Ana fonksiyon"""
    print("🤖 CompTIA TikTok Otomasyon Botu v2.0")
    print("=" * 45)
    print("\n✨ YENİ ÖZELLİKLER:")
    print("• 📸 Beğenilen videolar otomatik screenshot")
    print("• 📁 Session klasörü (timestamp bazlı)")
    print("• 📄 Detaylı JSON log ve raporlar")
    print("• 🎯 CompTIA içerik analizi")
    print("• 🤖 Doğal davranış simülasyonu")
    print()
    
    print("Oturum süreleri:")
    print("1. Test (2 dakika)")
    print("2. Hızlı (5 dakika)")
    print("3. Normal (10 dakika)")
    print("4. Uzun (15 dakika)")
    print("5. Maraton (30 dakika)")
    
    choice = input("\nSeçiminiz (1-5): ")
    
    duration_map = {
        '1': 2,
        '2': 5,
        '3': 10,
        '4': 15,
        '5': 30
    }
    
    duration = duration_map.get(choice, 5)
    
    print(f"\n🚀 {duration} dakikalık oturum hazırlanıyor...")
    print("📁 Session klasörü oluşturuluyor...")
    print("📸 Screenshot sistemi aktif...")
    print("🎯 CompTIA tespit sistemi hazır...")
    time.sleep(2)
    
    bot = CompTIATikTokBot()
    
    try:
        bot.run_session(duration)
    except KeyboardInterrupt:
        print("\n\n⚠️ Oturum manuel olarak durduruldu!")
        if bot.session_folder:
            bot.print_session_report()
        else:
            print("Session klasörü oluşturulmadan önce durduruldu.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        if bot.session_folder:
            bot.print_session_report()
        else:
            print("Session başlatılamadı.")

if __name__ == "__main__":
    main()