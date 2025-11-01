import pyautogui
import platform
import subprocess
import time
from typing import Optional, Dict, Any

class ApplicationController:
    def __init__(self):
        self.os_name = platform.system()
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        self.common_commands = {
            'type': self._type_text,
            'press': self._press_key,
            'hotkey': self._press_hotkey,
            'click': self._click,
            'double_click': self._double_click,
            'right_click': self._right_click,
            'scroll_up': self._scroll_up,
            'scroll_down': self._scroll_down,
            'move_mouse': self._move_mouse,
            'drag': self._drag,
            'screenshot': self._screenshot,
        }
        
        self.app_specific_commands = {
            'vscode': self._vscode_commands,
            'visual studio code': self._vscode_commands,
            'code': self._vscode_commands,
            'chrome': self._browser_commands,
            'firefox': self._browser_commands,
            'brave': self._browser_commands,
            'edge': self._browser_commands,
            'browser': self._browser_commands,
            'spotify': self._media_commands,
            'vlc': self._media_commands,
            'terminal': self._terminal_commands,
            'cmd': self._terminal_commands,
            'command prompt': self._terminal_commands,
            'powershell': self._terminal_commands,
            'notepad': self._editor_commands,
            'gedit': self._editor_commands,
            'textedit': self._editor_commands,
            'word': self._word_commands,
            'excel': self._excel_commands,
            'powerpoint': self._powerpoint_commands,
            'libreoffice': self._libreoffice_commands,
        }

    def execute_command(self, app_name: str, command: str, params: Dict[str, Any] = None) -> bool:
        try:
            params = params or {}
            command_lower = command.lower().strip()
            app_lower = app_name.lower().strip()
            
            if command_lower in self.common_commands:
                return self.common_commands[command_lower](params)
            
            for app_key, handler in self.app_specific_commands.items():
                if app_key in app_lower:
                    return handler(command_lower, params)
            
            return self._generic_command(command_lower, params)
            
        except Exception as e:
            print(f"Command execution failed: {e}")
            return False

    def _type_text(self, params: Dict[str, Any]) -> bool:
        text = params.get('text', '')
        if text:
            pyautogui.write(text, interval=0.05)
            return True
        return False

    def _press_key(self, params: Dict[str, Any]) -> bool:
        key = params.get('key', '')
        if key:
            pyautogui.press(key)
            return True
        return False

    def _press_hotkey(self, params: Dict[str, Any]) -> bool:
        keys = params.get('keys', [])
        if keys:
            pyautogui.hotkey(*keys)
            return True
        return False

    def _click(self, params: Dict[str, Any]) -> bool:
        x = params.get('x')
        y = params.get('y')
        if x is not None and y is not None:
            pyautogui.click(x, y)
        else:
            pyautogui.click()
        return True

    def _double_click(self, params: Dict[str, Any]) -> bool:
        x = params.get('x')
        y = params.get('y')
        if x is not None and y is not None:
            pyautogui.doubleClick(x, y)
        else:
            pyautogui.doubleClick()
        return True

    def _right_click(self, params: Dict[str, Any]) -> bool:
        x = params.get('x')
        y = params.get('y')
        if x is not None and y is not None:
            pyautogui.rightClick(x, y)
        else:
            pyautogui.rightClick()
        return True

    def _scroll_up(self, params: Dict[str, Any]) -> bool:
        amount = params.get('amount', 3)
        pyautogui.scroll(amount * 100)
        return True

    def _scroll_down(self, params: Dict[str, Any]) -> bool:
        amount = params.get('amount', 3)
        pyautogui.scroll(-amount * 100)
        return True

    def _move_mouse(self, params: Dict[str, Any]) -> bool:
        x = params.get('x')
        y = params.get('y')
        duration = params.get('duration', 0.5)
        if x is not None and y is not None:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        return False

    def _drag(self, params: Dict[str, Any]) -> bool:
        x = params.get('x')
        y = params.get('y')
        duration = params.get('duration', 0.5)
        if x is not None and y is not None:
            pyautogui.drag(x, y, duration=duration)
            return True
        return False

    def _screenshot(self, params: Dict[str, Any]) -> bool:
        filename = params.get('filename', 'screenshot.png')
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"Screenshot saved: {filename}")
        return True

    def _vscode_commands(self, command: str, params: Dict[str, Any]) -> bool:
        ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
        
        commands = {
            'save': lambda: pyautogui.hotkey(ctrl_or_cmd, 's'),
            'save all': lambda: pyautogui.hotkey(ctrl_or_cmd, 'k', 's'),
            'open file': lambda: pyautogui.hotkey(ctrl_or_cmd, 'o'),
            'new file': lambda: pyautogui.hotkey(ctrl_or_cmd, 'n'),
            'close': lambda: pyautogui.hotkey(ctrl_or_cmd, 'w'),
            'close all': lambda: pyautogui.hotkey(ctrl_or_cmd, 'k', 'w'),
            'find': lambda: pyautogui.hotkey(ctrl_or_cmd, 'f'),
            'replace': lambda: pyautogui.hotkey(ctrl_or_cmd, 'h'),
            'comment': lambda: pyautogui.hotkey(ctrl_or_cmd, '/'),
            'terminal': lambda: pyautogui.hotkey(ctrl_or_cmd, '`'),
            'command palette': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 'p'),
            'go to line': lambda: pyautogui.hotkey(ctrl_or_cmd, 'g'),
            'duplicate line': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 'd'),
            'delete line': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 'k'),
            'format document': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 'i'),
            'next tab': lambda: pyautogui.hotkey(ctrl_or_cmd, 'pagedown'),
            'previous tab': lambda: pyautogui.hotkey(ctrl_or_cmd, 'pageup'),
            'split editor': lambda: pyautogui.hotkey(ctrl_or_cmd, '\\'),
        }
        
        if command in commands:
            commands[command]()
            return True
        return False

    def _browser_commands(self, command: str, params: Dict[str, Any]) -> bool:
        ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
        
        commands = {
            'new tab': lambda: pyautogui.hotkey(ctrl_or_cmd, 't'),
            'close tab': lambda: pyautogui.hotkey(ctrl_or_cmd, 'w'),
            'reopen tab': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 't'),
            'next tab': lambda: pyautogui.hotkey(ctrl_or_cmd, 'tab'),
            'previous tab': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 'tab'),
            'refresh': lambda: pyautogui.hotkey(ctrl_or_cmd, 'r'),
            'hard refresh': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 'r'),
            'back': lambda: pyautogui.hotkey('alt', 'left'),
            'forward': lambda: pyautogui.hotkey('alt', 'right'),
            'home': lambda: pyautogui.hotkey('alt', 'home'),
            'address bar': lambda: pyautogui.hotkey(ctrl_or_cmd, 'l'),
            'bookmark': lambda: pyautogui.hotkey(ctrl_or_cmd, 'd'),
            'history': lambda: pyautogui.hotkey(ctrl_or_cmd, 'h'),
            'downloads': lambda: pyautogui.hotkey(ctrl_or_cmd, 'j'),
            'incognito': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 'n'),
            'developer tools': lambda: pyautogui.hotkey('f12'),
            'zoom in': lambda: pyautogui.hotkey(ctrl_or_cmd, '+'),
            'zoom out': lambda: pyautogui.hotkey(ctrl_or_cmd, '-'),
            'reset zoom': lambda: pyautogui.hotkey(ctrl_or_cmd, '0'),
            'fullscreen': lambda: pyautogui.press('f11'),
        }
        
        if command in commands:
            commands[command]()
            return True
        return False

    def _media_commands(self, command: str, params: Dict[str, Any]) -> bool:
        commands = {
            'play': lambda: pyautogui.press('space'),
            'pause': lambda: pyautogui.press('space'),
            'next': lambda: pyautogui.press('n'),
            'previous': lambda: pyautogui.press('p'),
            'volume up': lambda: pyautogui.press('volumeup'),
            'volume down': lambda: pyautogui.press('volumedown'),
            'mute': lambda: pyautogui.press('volumemute'),
            'fullscreen': lambda: pyautogui.press('f'),
            'seek forward': lambda: pyautogui.press('right'),
            'seek backward': lambda: pyautogui.press('left'),
        }
        
        if command in commands:
            commands[command]()
            return True
        return False

    def _terminal_commands(self, command: str, params: Dict[str, Any]) -> bool:
        ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
        
        commands = {
            'clear': lambda: (pyautogui.write('clear') and pyautogui.press('enter')),
            'new tab': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 't'),
            'close tab': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 'w'),
            'copy': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 'c'),
            'paste': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 'v'),
            'interrupt': lambda: pyautogui.hotkey(ctrl_or_cmd, 'c'),
            'zoom in': lambda: pyautogui.hotkey(ctrl_or_cmd, '+'),
            'zoom out': lambda: pyautogui.hotkey(ctrl_or_cmd, '-'),
        }
        
        if command in commands:
            commands[command]()
            return True
        return False

    def _editor_commands(self, command: str, params: Dict[str, Any]) -> bool:
        ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
        
        commands = {
            'save': lambda: pyautogui.hotkey(ctrl_or_cmd, 's'),
            'save as': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', 's'),
            'open': lambda: pyautogui.hotkey(ctrl_or_cmd, 'o'),
            'new': lambda: pyautogui.hotkey(ctrl_or_cmd, 'n'),
            'find': lambda: pyautogui.hotkey(ctrl_or_cmd, 'f'),
            'replace': lambda: pyautogui.hotkey(ctrl_or_cmd, 'h'),
            'select all': lambda: pyautogui.hotkey(ctrl_or_cmd, 'a'),
            'copy': lambda: pyautogui.hotkey(ctrl_or_cmd, 'c'),
            'cut': lambda: pyautogui.hotkey(ctrl_or_cmd, 'x'),
            'paste': lambda: pyautogui.hotkey(ctrl_or_cmd, 'v'),
            'undo': lambda: pyautogui.hotkey(ctrl_or_cmd, 'z'),
            'redo': lambda: pyautogui.hotkey(ctrl_or_cmd, 'y'),
        }
        
        if command in commands:
            commands[command]()
            return True
        return False

    def _word_commands(self, command: str, params: Dict[str, Any]) -> bool:
        ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
        
        commands = {
            'bold': lambda: pyautogui.hotkey(ctrl_or_cmd, 'b'),
            'italic': lambda: pyautogui.hotkey(ctrl_or_cmd, 'i'),
            'underline': lambda: pyautogui.hotkey(ctrl_or_cmd, 'u'),
            'align left': lambda: pyautogui.hotkey(ctrl_or_cmd, 'l'),
            'align center': lambda: pyautogui.hotkey(ctrl_or_cmd, 'e'),
            'align right': lambda: pyautogui.hotkey(ctrl_or_cmd, 'r'),
            'justify': lambda: pyautogui.hotkey(ctrl_or_cmd, 'j'),
            'increase font': lambda: pyautogui.hotkey(ctrl_or_cmd, ']'),
            'decrease font': lambda: pyautogui.hotkey(ctrl_or_cmd, '['),
        }
        
        if command in commands:
            commands[command]()
            return True
        return self._editor_commands(command, params)

    def _excel_commands(self, command: str, params: Dict[str, Any]) -> bool:
        ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
        
        commands = {
            'new sheet': lambda: pyautogui.hotkey('shift', 'f11'),
            'insert row': lambda: pyautogui.hotkey(ctrl_or_cmd, 'shift', '+'),
            'delete row': lambda: pyautogui.hotkey(ctrl_or_cmd, '-'),
            'autosum': lambda: pyautogui.hotkey('alt', '='),
            'format cells': lambda: pyautogui.hotkey(ctrl_or_cmd, '1'),
        }
        
        if command in commands:
            commands[command]()
            return True
        return self._editor_commands(command, params)

    def _powerpoint_commands(self, command: str, params: Dict[str, Any]) -> bool:
        ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
        
        commands = {
            'new slide': lambda: pyautogui.hotkey(ctrl_or_cmd, 'm'),
            'start presentation': lambda: pyautogui.press('f5'),
            'next slide': lambda: pyautogui.press('right'),
            'previous slide': lambda: pyautogui.press('left'),
            'end presentation': lambda: pyautogui.press('esc'),
        }
        
        if command in commands:
            commands[command]()
            return True
        return self._editor_commands(command, params)

    def _libreoffice_commands(self, command: str, params: Dict[str, Any]) -> bool:
        return self._editor_commands(command, params)

    def _generic_command(self, command: str, params: Dict[str, Any]) -> bool:
        text = params.get('text', '')
        
        if 'type' in command or 'write' in command:
            if text:
                pyautogui.write(text, interval=0.05)
                return True
        
        elif 'enter' in command or 'return' in command:
            pyautogui.press('enter')
            return True
        
        elif 'delete' in command or 'backspace' in command:
            pyautogui.press('backspace')
            return True
        
        elif 'tab' in command:
            pyautogui.press('tab')
            return True
        
        elif 'escape' in command or 'esc' in command:
            pyautogui.press('esc')
            return True
        
        elif 'copy' in command:
            ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
            pyautogui.hotkey(ctrl_or_cmd, 'c')
            return True
        
        elif 'paste' in command:
            ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
            pyautogui.hotkey(ctrl_or_cmd, 'v')
            return True
        
        elif 'cut' in command:
            ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
            pyautogui.hotkey(ctrl_or_cmd, 'x')
            return True
        
        elif 'select all' in command:
            ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
            pyautogui.hotkey(ctrl_or_cmd, 'a')
            return True
        
        elif 'save' in command:
            ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
            pyautogui.hotkey(ctrl_or_cmd, 's')
            return True
        
        elif 'undo' in command:
            ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
            pyautogui.hotkey(ctrl_or_cmd, 'z')
            return True
        
        elif 'redo' in command:
            ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
            pyautogui.hotkey(ctrl_or_cmd, 'y')
            return True
        
        elif 'find' in command or 'search' in command:
            ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
            pyautogui.hotkey(ctrl_or_cmd, 'f')
            return True
        
        elif 'close' in command or 'quit' in command:
            ctrl_or_cmd = 'command' if self.os_name == 'Darwin' else 'ctrl'
            pyautogui.hotkey('alt' if self.os_name != 'Darwin' else ctrl_or_cmd, 'f4' if self.os_name != 'Darwin' else 'q')
            return True
        
        return False

    def focus_application(self, app_name: str) -> bool:
        try:
            app_lower = app_name.lower()
            
            if self.os_name == 'Darwin':
                try:
                    script = f'tell application "{app_name}" to activate'
                    subprocess.run(['osascript', '-e', script], check=True, timeout=5)
                    return True
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    return False
            
            elif self.os_name == 'Windows':
                try:
                    import win32gui
                    import win32con
                    
                    def window_enum_callback(hwnd, windows):
                        try:
                            if win32gui.IsWindowVisible(hwnd):
                                title = win32gui.GetWindowText(hwnd).lower()
                                if app_lower in title:
                                    windows.append(hwnd)
                        except Exception:
                            pass
                        return True
                    
                    windows = []
                    win32gui.EnumWindows(window_enum_callback, windows)
                    
                    if windows:
                        hwnd = windows[0]
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                        return True
                except ImportError:
                    print("pywin32 not installed. Install with: pip install pywin32")
                    return False
                except Exception:
                    return False
            
            elif self.os_name == 'Linux':
                try:
                    result = subprocess.run(
                        ['wmctrl', '-a', app_name],
                        capture_output=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
                
                try:
                    result = subprocess.run(
                        ['xdotool', 'search', '--name', app_name, 'windowactivate'],
                        capture_output=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            
            return False
            
        except Exception as e:
            print(f"Failed to focus application: {e}")
            return False

