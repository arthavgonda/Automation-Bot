
import os
import platform
from pathlib import Path

def check_chrome_profile():
    print("\n" + "="*60)
    print("CHROME PROFILE CHECK")
    print("="*60)
    system = platform.system()
    if system == 'Windows':
        user_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data')
    elif system == 'Darwin':
        user_data_dir = os.path.join(str(Path.home()), 'Library', 'Application Support', 'Google', 'Chrome')
    else:
        paths_to_check = [
            os.path.join(str(Path.home()), '.config', 'google-chrome'),
            os.path.join(str(Path.home()), 'snap', 'chromium', 'current', '.config', 'chromium'),
            os.path.join(str(Path.home()), 'snap', 'chrome', 'current', '.config', 'google-chrome'),
        ]
        user_data_dir = None
        for path in paths_to_check:
            if os.path.exists(path):
                user_data_dir = path
                if 'snap' in path:
                    print("(Snap installation detected)")
                break
        if not user_data_dir:
            user_data_dir = os.path.join(str(Path.home()), '.config', 'google-chrome')
    print(f"Expected Chrome profile directory: {user_data_dir}")
    print(f"Directory exists: {os.path.exists(user_data_dir)}")
    if os.path.exists(user_data_dir):
        print("\nProfiles found:")
        try:
            items = os.listdir(user_data_dir)
            profiles = [item for item in items if os.path.isdir(os.path.join(user_data_dir, item)) 
                       and (item == 'Default' or item.startswith('Profile') or item == 'Automation' or item.startswith('Automation_'))]
            for profile in profiles:
                profile_path = os.path.join(user_data_dir, profile)
                print(f"  - {profile} ({profile_path})")
                prefs_file = os.path.join(profile_path, 'Preferences')
                if os.path.exists(prefs_file):
                    print(f"    ✓ Valid profile (Preferences file found)")
                    if profile == 'Automation' or profile.startswith('Automation_'):
                        print(f"    ⚙ Automation profile (can run alongside main browser)")
                else:
                    print(f"    ✗ Might be incomplete profile")
        except Exception as e:
            print(f"Error reading profiles: {e}")
    else:
        print("Chrome profile directory NOT FOUND")
    return user_data_dir

def check_brave_profile():
    print("\n" + "="*60)
    print("BRAVE PROFILE CHECK")
    print("="*60)
    system = platform.system()
    if system == 'Windows':
        user_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data')
    elif system == 'Darwin':
        user_data_dir = os.path.join(str(Path.home()), 'Library', 'Application Support', 'BraveSoftware', 'Brave-Browser')
    else:
        snap_dir = os.path.join(str(Path.home()), 'snap', 'brave', 'current', '.config', 'BraveSoftware', 'Brave-Browser')
        if os.path.exists(snap_dir):
            user_data_dir = snap_dir
            print("(Snap installation detected)")
        else:
            user_data_dir = os.path.join(str(Path.home()), '.config', 'BraveSoftware', 'Brave-Browser')
    print(f"Expected Brave profile directory: {user_data_dir}")
    print(f"Directory exists: {os.path.exists(user_data_dir)}")
    if os.path.exists(user_data_dir):
        print("\nProfiles found:")
        try:
            items = os.listdir(user_data_dir)
            profiles = [item for item in items if os.path.isdir(os.path.join(user_data_dir, item)) 
                       and (item == 'Default' or item.startswith('Profile') or item == 'Automation' or item.startswith('Automation_'))]
            for profile in profiles:
                profile_path = os.path.join(user_data_dir, profile)
                print(f"  - {profile} ({profile_path})")
                prefs_file = os.path.join(profile_path, 'Preferences')
                if os.path.exists(prefs_file):
                    print(f"    ✓ Valid profile (Preferences file found)")
                    if profile == 'Automation' or profile.startswith('Automation_'):
                        print(f"    ⚙ Automation profile (can run alongside main browser)")
                else:
                    print(f"    ✗ Might be incomplete profile")
        except Exception as e:
            print(f"Error reading profiles: {e}")
    else:
        print("Brave profile directory NOT FOUND")
    return user_data_dir

def check_chromium_profile():
    print("\n" + "="*60)
    print("CHROMIUM PROFILE CHECK")
    print("="*60)
    system = platform.system()
    if system == 'Windows':
        user_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Chromium', 'User Data')
    elif system == 'Darwin':
        user_data_dir = os.path.join(str(Path.home()), 'Library', 'Application Support', 'Chromium')
    else:
        paths_to_check = [
            os.path.join(str(Path.home()), '.config', 'chromium'),
            os.path.join(str(Path.home()), 'snap', 'chromium', 'current', '.config', 'chromium'),
            os.path.join(str(Path.home()), '.var', 'app', 'org.chromium.Chromium', 'config', 'chromium'),
        ]
        user_data_dir = None
        for path in paths_to_check:
            if os.path.exists(path):
                user_data_dir = path
                if 'snap' in path:
                    print("(Snap installation detected)")
                elif 'flatpak' in path or '.var' in path:
                    print("(Flatpak installation detected)")
                break
        if not user_data_dir:
            user_data_dir = os.path.join(str(Path.home()), '.config', 'chromium')
    print(f"Expected Chromium profile directory: {user_data_dir}")
    print(f"Directory exists: {os.path.exists(user_data_dir)}")
    if os.path.exists(user_data_dir):
        print("\nProfiles found:")
        try:
            items = os.listdir(user_data_dir)
            profiles = [item for item in items if os.path.isdir(os.path.join(user_data_dir, item)) 
                       and (item == 'Default' or item.startswith('Profile') or item == 'Automation' or item.startswith('Automation_'))]
            for profile in profiles:
                profile_path = os.path.join(user_data_dir, profile)
                print(f"  - {profile} ({profile_path})")
                prefs_file = os.path.join(profile_path, 'Preferences')
                if os.path.exists(prefs_file):
                    print(f"    ✓ Valid profile (Preferences file found)")
                    if profile == 'Automation' or profile.startswith('Automation_'):
                        print(f"    ⚙ Automation profile (can run alongside main browser)")
                else:
                    print(f"    ✗ Might be incomplete profile")
        except Exception as e:
            print(f"Error reading profiles: {e}")
    else:
        print("Chromium profile directory NOT FOUND")
    return user_data_dir

def check_firefox_profile():
    print("\n" + "="*60)
    print("FIREFOX PROFILE CHECK")
    print("="*60)
    system = platform.system()
    if system == 'Windows':
        firefox_profile_path = os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles')
    elif system == 'Darwin':
        firefox_profile_path = os.path.join(str(Path.home()), 'Library', 'Application Support', 'Firefox', 'Profiles')
    else:
        snap_dir = os.path.join(str(Path.home()), 'snap', 'firefox', 'common', '.mozilla', 'firefox')
        if os.path.exists(snap_dir):
            firefox_profile_path = snap_dir
            print("(Snap installation detected)")
        else:
            firefox_profile_path = os.path.join(str(Path.home()), '.mozilla', 'firefox')
    print(f"Expected Firefox profile directory: {firefox_profile_path}")
    print(f"Directory exists: {os.path.exists(firefox_profile_path)}")
    if os.path.exists(firefox_profile_path):
        print("\nProfiles found:")
        try:
            items = os.listdir(firefox_profile_path)
            profiles = [item for item in items if os.path.isdir(os.path.join(firefox_profile_path, item))]
            for profile in profiles:
                profile_path = os.path.join(firefox_profile_path, profile)
                print(f"  - {profile} ({profile_path})")
                if 'default' in profile.lower():
                    print(f"    ✓ This appears to be a default profile")
        except Exception as e:
            print(f"Error reading profiles: {e}")
    else:
        print("Firefox profile directory NOT FOUND")
    return firefox_profile_path

def main():
    print("\n" + "="*60)
    print("BROWSER PROFILE DIAGNOSTIC TOOL")
    print("="*60)
    print(f"Operating System: {platform.system()}")
    print(f"Home Directory: {Path.home()}")
    check_chrome_profile()
    check_brave_profile()
    check_chromium_profile()
    check_firefox_profile()
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    print("1. If a profile directory is found, the path is correct")
    print("2. Automation uses a separate 'Automation' profile")
    print("3. ✓ Your browser can stay open while automation runs!")
    print("4. The 'Automation' profile will be created automatically if needed")
    print("5. This profile works alongside your main browser profile")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()