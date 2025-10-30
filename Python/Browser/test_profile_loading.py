
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from Browser.DriverManager import DriverManager
import time

def test_brave_profile():
    print("\n" + "="*60)
    print("TESTING BRAVE WITH AUTOMATION PROFILE")
    print("="*60)
    print("\n✓ Note: Your browser can stay open!")
    print("  Automation uses a separate 'Automation' profile")
    input("Press Enter to continue...")
    try:
        manager = DriverManager()
        driver = manager.get_brave_driver()
        if driver:
            print("\n✅ Brave driver initialized successfully!")
            print("Opening a test page...")
            driver.get("https://www.example.com")
            time.sleep(3)
            print("\n📋 Please verify:")
            print("1. Browser opened successfully")
            print("2. Page loaded correctly")
            print("3. No errors occurred")
            print("\nNote: This uses an 'Automation' profile separate from your main browser.")
            print("Your main browser can continue running normally!")
            input("\nPress Enter to close the automation browser...")
            driver.quit()
            print("✅ Test completed!")
        else:
            print("❌ Failed to initialize Brave driver")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_firefox_profile():
    print("\n" + "="*60)
    print("TESTING FIREFOX WITH AUTOMATION PROFILE")
    print("="*60)
    print("\n✓ Note: Your browser can stay open!")
    print("  Automation uses a separate profile")
    input("Press Enter to continue...")
    try:
        manager = DriverManager()
        driver = manager.get_firefox_driver()
        if driver:
            print("\n✅ Firefox driver initialized successfully!")
            print("Opening a test page...")
            driver.get("https://www.example.com")
            time.sleep(3)
            print("\n📋 Please verify:")
            print("1. Browser opened successfully")
            print("2. Page loaded correctly")
            print("3. No errors occurred")
            print("\nNote: This uses an 'Automation' profile separate from your main browser.")
            print("Your main browser can continue running normally!")
            input("\nPress Enter to close the automation browser...")
            driver.quit()
            print("✅ Test completed!")
        else:
            print("❌ Failed to initialize Firefox driver")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n" + "="*60)
    print("BROWSER PROFILE LOADING TEST")
    print("="*60)
    print("\nThis script will test if the browser opens with the automation profile.")
    print("\n✓ Good news: Your browser can stay open!")
    print("  Automation uses a separate 'Automation' profile that works alongside your main browser.")
    print("\nWhich browser would you like to test?")
    print("1. Brave")
    print("2. Firefox")
    print("3. Both")
    print("4. Exit")
    choice = input("\nEnter your choice (1-4): ")
    if choice == '1':
        test_brave_profile()
    elif choice == '2':
        test_firefox_profile()
    elif choice == '3':
        test_brave_profile()
        test_firefox_profile()
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()