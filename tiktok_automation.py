#!/usr/bin/env python3
import subprocess
import time
import random

class TikTokAutomation:
    def __init__(self, adb_path="/mnt/c/Users/canga/Desktop/platform-tools/adb.exe"):
        self.adb_path = adb_path
        # Samsung S20 screen dimensions (1440x3200, but scaled to 1080x2400 typically)
        self.screen_width = 1080
        self.screen_height = 2400
        
        # TikTok UI coordinates (based on actual phone measurements)
        self.like_button = (994, 1136)  # Like button (heart)
        self.comment_button = (964, 1344)  # Comment button
        self.share_button = (950, 1500)  # Share button (estimated)
        
        # Random variation range for natural behavior
        self.random_range = 15  # pixels
        
        # Swipe area for scrolling videos
        self.swipe_start = (540, 1800)
        self.swipe_end = (540, 800)

    def run_adb_command(self, command):
        """ADB komutu çalıştır"""
        full_command = [self.adb_path] + command
        try:
            result = subprocess.run(full_command, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Hata: {e}")
            return False

    def tap(self, x, y, add_randomness=True):
        """Tap at screen coordinates with optional randomness"""
        if add_randomness:
            # Add random variation to make it look natural
            random_x = x + random.randint(-self.random_range, self.random_range)
            random_y = y + random.randint(-self.random_range, self.random_range)
            
            # Keep within screen bounds
            random_x = max(0, min(random_x, self.screen_width))
            random_y = max(0, min(random_y, self.screen_height))
            
            return self.run_adb_command(['shell', 'input', 'tap', str(random_x), str(random_y)])
        else:
            return self.run_adb_command(['shell', 'input', 'tap', str(x), str(y)])

    def swipe_up(self):
        """Swipe up to next video with random variation"""
        # Add randomness to swipe coordinates
        start_x = self.swipe_start[0] + random.randint(-30, 30)
        start_y = self.swipe_start[1] + random.randint(-20, 20)
        end_x = self.swipe_end[0] + random.randint(-30, 30)
        end_y = self.swipe_end[1] + random.randint(-20, 20)
        
        # Random swipe duration (250-400ms)
        duration = random.randint(250, 400)
        
        return self.run_adb_command([
            'shell', 'input', 'swipe', 
            str(start_x), str(start_y),
            str(end_x), str(end_y),
            str(duration)
        ])

    def like_video(self):
        """Like the current video with random tap variation"""
        print("Liking video...")
        return self.tap(self.like_button[0], self.like_button[1], add_randomness=True)

    def open_comments(self):
        """Open comments section with random tap variation"""
        print("Opening comments...")
        return self.tap(self.comment_button[0], self.comment_button[1], add_randomness=True)

    def close_comments(self):
        """Close comments (back button)"""
        return self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_BACK'])

    def open_tiktok(self):
        """Open TikTok application"""
        print("Opening TikTok...")
        return self.run_adb_command([
            'shell', 'monkey', '-p', 'com.zhiliaoapp.musically', '-c', 
            'android.intent.category.LAUNCHER', '1'
        ])

    def wait_random(self, min_sec=1, max_sec=3):
        """Random wait time"""
        wait_time = random.uniform(min_sec, max_sec)
        print(f"Waiting {wait_time:.1f} seconds...")
        time.sleep(wait_time)

    def automate_session(self, duration_minutes=5):
        """Automated TikTok session"""
        print(f"Starting {duration_minutes} minute automation session...")
        
        # TikTok'u aç
        self.open_tiktok()
        self.wait_random(3, 5)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        video_count = 0
        
        while time.time() < end_time:
            video_count += 1
            print(f"\n--- Video {video_count} ---")
            
            # Random activities
            actions = []
            
            # 60-80% chance to watch video (varies)
            watch_chance = random.uniform(0.6, 0.8)
            if random.random() < watch_chance:
                watch_time = random.uniform(2, 12)  # More varied watch times
                print(f"Watching video for {watch_time:.1f} seconds...")
                time.sleep(watch_time)
            
            # 25-35% chance to like (random percentage each time)
            like_chance = random.uniform(0.25, 0.35)
            if random.random() < like_chance:
                self.like_video()
                self.wait_random(0.5, 2.0)
            
            # 15-25% chance to check comments (random percentage)
            comment_chance = random.uniform(0.15, 0.25)
            if random.random() < comment_chance:
                self.open_comments()
                self.wait_random(2, 5)  # Random time looking at comments
                self.close_comments()
                self.wait_random(1, 3)
            
            # Go to next video
            self.swipe_up()
            self.wait_random(0.8, 4.0)  # More varied pause between videos
        
        print(f"\nAutomation completed! Watched {video_count} videos.")

if __name__ == "__main__":
    # Windows ADB path
    automation = TikTokAutomation()
    
    print("TikTok Automation")
    print("1. Manual test")
    print("2. Auto session (5 minutes)")
    print("3. Long session (15 minutes)")
    
    choice = input("Your choice (1-3): ")
    
    if choice == "1":
        print("\nStarting manual test...")
        automation.open_tiktok()
        time.sleep(3)
        automation.swipe_up()
        time.sleep(2)
        automation.like_video()
    elif choice == "2":
        automation.automate_session(5)
    elif choice == "3":
        automation.automate_session(15)
    else:
        print("Invalid choice!")