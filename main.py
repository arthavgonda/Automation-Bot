import sys
import os
import subprocess
import venv
from pathlib import Path

def get_venv_python():
    if sys.platform == "win32":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")

def is_venv_active():
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

def setup_and_activate_venv():
    venv_path = Path("venv")
    venv_python = get_venv_python()
    if is_venv_active():
        return True
    print("\n" + "="*60)
    print("VIRTUAL ENVIRONMENT SETUP")
    print("="*60 + "\n")
    if not venv_path.exists():
        print("Creating virtual environment...")
        try:
            venv.create("venv", with_pip=True)
            print("Virtual environment created\n")
        except Exception as e:
            print(f"Error creating virtual environment: {e}")
            return False
    else:
        print("Virtual environment already exists\n")
    requirements_file = Path("requirements.txt")
    needs_install = False
    if requirements_file.exists():
        print("Checking dependencies...")
        try:
            result = subprocess.run(
                [venv_python, "-c", "import vosk; import whisper; import selenium"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                needs_install = True
        except:
            needs_install = True
    if needs_install and requirements_file.exists():
        print("Installing dependencies...\n")
        try:
            subprocess.run(
                [venv_python, "-m", "pip", "install", "--upgrade", "pip"],
                check=True
            )
            subprocess.run(
                [venv_python, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True
            )
            subprocess.run(
                [venv_python, "-m", "pip", "install", "selenium", "webdriver-manager"],
                check=True
            )
            print("\nAll dependencies installed\n")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return False
    elif not needs_install:
        print("All dependencies already installed\n")
    print("Restarting in virtual environment...\n")
    print("="*60 + "\n")
    try:
        script_path = os.path.abspath(__file__)
        os.execv(venv_python, [venv_python, script_path] + sys.argv[1:])
    except Exception as e:
        print(f"Error restarting script: {e}")
        return False

if __name__ == "__main__":
    if not is_venv_active():
        setup_and_activate_venv()
        sys.exit(0)

from STT.RTMicroPhone import stream_microPhone
from STT.sttOffline import stt_vosk
from STT.sttWhisper import stt_whisper
from STT.NetworkStatus import check_server_connectivity
from Browser.DriverManager import setup_driver
from Browser.IntelligentBrowser import process_voice_command
from System.SystemController import SystemController
import queue

browser_driver = None
system_controller = None
command_queue = queue.Queue()

def stt_with_actions(audio_np):
    global browser_driver, system_controller
    network_available = check_server_connectivity("8.8.8.8", 53, 3)
    if network_available and browser_driver:
        transcription = stt_whisper(audio_np)
    elif network_available:
        transcription = stt_whisper(audio_np)
    else:
        transcription = stt_vosk(audio_np)
    if transcription and transcription.strip():
        if browser_driver and system_controller:
            result = process_voice_command(browser_driver, system_controller, transcription)
            if result == "EXIT":
                browser_driver = None
        elif system_controller:
            from Browser.IntelligentBrowser import EnhancedIntelligentBrowser
            class DummyDriver:
                def get(self, url): pass
                def quit(self): pass
            dummy = DummyDriver()
            temp_browser = EnhancedIntelligentBrowser(dummy, system_controller)
            temp_browser.execute_command(transcription)
    return transcription

def print_help():
    print("\n" + "="*60)
    print("AVAILABLE VOICE COMMANDS")
    print("="*60)
    print("\nBrowser Commands:")
    print("search for [query] - Search Google")
    print("open youtube.com - Open website")
    print("download steam - Download application")
    print("get discord - Download Discord")
    print("\nInstallation Commands:")
    print("install [app] - Smart install (offers options)")
    print("terminal install git - Install via package manager")
    print("open app store - Open native app store")
    print("\nFile Operations:")
    print("create folder MyFolder - Create folder")
    print("delete folder TestFolder - Delete folder")
    print("create file test.txt - Create file")
    print("delete file test.txt - Delete file")
    print("list files - List files in home directory")
    print("list files in Documents - List files in Documents")
    print("\nSystem Commands:")
    print("system info - Show system information")
    print("exit or close browser - Quit program")
    print("="*60 + "\n")

def main():
    global browser_driver, system_controller
    print("\n" + "="*60)
    print("VOICE-CONTROLLED SYSTEM AUTOMATION")
    print("="*60)
    print("\nInitializing system...")
    system_controller = SystemController()
    print("System controller initialized")
    network_available = check_server_connectivity("8.8.8.8", 53, 3)
    if network_available:
        print("Network available - Using Whisper (GPU)")
        stt_function = stt_whisper
    else:
        print("Network unavailable - Using Vosk (offline)")
        stt_function = stt_vosk
    system_controller.get_system_info()
    print("\n" + "="*60)
    print("BROWSER SETUP")
    print("="*60)
    print("\nBrowser automation enables web searches and downloads.")
    print("System operations (file/folder management) work without browser.")
    response = input("\nEnable browser automation? (y/n): ").lower()
    if response == 'y':
        browser_driver = setup_driver()
        if browser_driver:
            print("\nBrowser automation enabled!")
        else:
            print("\nBrowser automation disabled - continuing with system operations only")
    else:
        print("\nBrowser automation disabled - system operations only")
    print_help()
    print("\n" + "="*60)
    print("STARTING VOICE RECOGNITION")
    print("="*60 + "\n")
    try:
        stream_microPhone(stt_with_actions, buffer_seconds=3)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        if browser_driver:
            print("Closing browser...")
            try:
                browser_driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()