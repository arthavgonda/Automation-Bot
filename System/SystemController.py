import os
import platform
import subprocess
import shutil
from pathlib import Path

class SystemController:
    
    def __init__(self):
        self.system = platform.system()
        self.home_dir = Path.home()
        
    def create_folder(self, folder_path):
        try:
            if not os.path.isabs(folder_path):
                folder_path = self.home_dir / folder_path
            else:
                folder_path = Path(folder_path)
            
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"Folder created: {folder_path}")
            return True
        except Exception as e:
            print(f"Failed to create folder: {e}")
            return False
    
    def delete_folder(self, folder_path):
        try:
            if not os.path.isabs(folder_path):
                folder_path = self.home_dir / folder_path
            else:
                folder_path = Path(folder_path)
            
            if not folder_path.exists():
                print(f"Folder does not exist: {folder_path}")
                return False
            
            critical_paths = [
                self.home_dir,
                Path("/"),
                Path("C:\\") if self.system == "Windows" else None,
                self.home_dir / "Documents",
                self.home_dir / "Desktop",
            ]
            
            if folder_path in [p for p in critical_paths if p]:
                print(f"Cannot delete critical system folder: {folder_path}")
                return False
            
            shutil.rmtree(folder_path)
            print(f"Folder deleted: {folder_path}")
            return True
        except Exception as e:
            print(f"Failed to delete folder: {e}")
            return False
    
    def create_file(self, file_path, content=""):
        try:
            if not os.path.isabs(file_path):
                file_path = self.home_dir / file_path
            else:
                file_path = Path(file_path)
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"File created: {file_path}")
            return True
        except Exception as e:
            print(f"Failed to create file: {e}")
            return False
    
    def delete_file(self, file_path):
        try:
            if not os.path.isabs(file_path):
                file_path = self.home_dir / file_path
            else:
                file_path = Path(file_path)
            
            if not file_path.exists():
                print(f"File does not exist: {file_path}")
                return False
            
            if not file_path.is_file():
                print(f"Not a file: {file_path}")
                return False
            
            file_path.unlink()
            print(f"File deleted: {file_path}")
            return True
        except Exception as e:
            print(f"Failed to delete file: {e}")
            return False
    
    def install_app_terminal(self, app_name):
        print(f"Installing {app_name} via package manager...")
        
        try:
            if self.system == "Linux":
                return self._install_linux(app_name)
            elif self.system == "Darwin":
                return self._install_macos(app_name)
            elif self.system == "Windows":
                return self._install_windows(app_name)
            else:
                print(f"Unsupported system: {self.system}")
                return False
        except Exception as e:
            print(f"Error during installation: {e}")
            return False
    
    def _install_linux(self, app_name):
        print("Linux detected")
        
        managers = [
            ("apt", ["sudo", "apt", "install", "-y", app_name]),
            ("dnf", ["sudo", "dnf", "install", "-y", app_name]),
            ("yum", ["sudo", "yum", "install", "-y", app_name]),
            ("pacman", ["sudo", "pacman", "-S", "--noconfirm", app_name]),
            ("zypper", ["sudo", "zypper", "install", "-y", app_name]),
            ("apk", ["sudo", "apk", "add", app_name]),
            ("snap", ["sudo", "snap", "install", app_name]),
            ("flatpak", ["flatpak", "install", "-y", "flathub", app_name]),
        ]
        
        for manager, cmd in managers:
            if shutil.which(manager):
                print(f"Using {manager}...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{app_name} installed successfully via {manager}!")
                    return True
                else:
                    print(f"{manager} install failed")
        
        print(f"Could not install {app_name} on Linux")
        return False
    
    def _install_macos(self, app_name):
        print("macOS detected")
        
        if shutil.which("brew"):
            print("Using Homebrew...")
            result = subprocess.run(
                ["brew", "install", app_name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"{app_name} installed successfully via Homebrew!")
                return True
            else:
                print("Homebrew install failed")
        else:
            print("Homebrew not found")
            print("\nTo install Homebrew, run:")
            print('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        
        print(f"Could not install {app_name} via package manager")
        return False
    
    def _install_windows(self, app_name):
        print("Windows detected")
        
        if shutil.which("choco"):
            print("Using Chocolatey...")
            result = subprocess.run(
                ["choco", "install", app_name, "-y"],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                print(f"{app_name} installed successfully via chocolatey!")
                return True
            else:
                print(f"Chocolatey install failed")
        else:
            print("Chocolatey not found")
            print("\nTo install Chocolatey, run PowerShell as Admin:")
            print('Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString("https://community.chocolatey.org/install.ps1"))')
        
        print(f"Could not install {app_name} via any package manager")
        return False
    
    def open_app_store(self):
        try:
            if self.system == "Darwin":
                print("Opening Mac App Store...")
                subprocess.run(["open", "macappstore://"])
                return True
            
            elif self.system == "Windows":
                print("Opening Microsoft Store...")
                subprocess.run(["start", "ms-windows-store://"], shell=True)
                return True
            
            elif self.system == "Linux":
                stores = [
                    ("snap-store", "Snap Store"),
                    ("gnome-software", "GNOME Software"),
                    ("plasma-discover", "KDE Discover"),
                ]
                
                for cmd, name in stores:
                    if shutil.which(cmd):
                        print(f"Opening {name}...")
                        subprocess.Popen([cmd])
                        return True
                
                print("No app store found on this Linux system")
                return False
            
            return False
        except Exception as e:
            print(f"Failed to open app store: {e}")
            return False
    
    def list_files(self, directory=None):
        try:
            if directory is None:
                directory = self.home_dir
            elif not os.path.isabs(directory):
                directory = self.home_dir / directory
            else:
                directory = Path(directory)
            
            if not directory.exists():
                print(f"Directory does not exist: {directory}")
                return False
            
            print(f"\nContents of {directory}:")
            print("="*60)
            
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                if item.is_dir():
                    print(f"{item.name}/")
                else:
                    size = item.stat().st_size
                    size_str = self._format_size(size)
                    print(f"{item.name} ({size_str})")
            
            print("="*60 + "\n")
            return True
        except Exception as e:
            print(f"Failed to list files: {e}")
            return False
    
    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_system_info(self):
        info = {
            "system": self.system,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "home_directory": str(self.home_dir),
        }
        
        print("\nSystem Information:")
        print("="*60)
        for key, value in info.items():
            print(f"{key}: {value}")
        print("="*60 + "\n")
        
        return info