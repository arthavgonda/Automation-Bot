from typing import Optional, Dict, Any
import time

class ContextManager:
    def __init__(self):
        self.current_app: Optional[str] = None
        self.previous_app: Optional[str] = None
        self.app_history: list = []
        self.context_start_time: Optional[float] = None
        self.app_states: Dict[str, Dict[str, Any]] = {}
        
    def set_context(self, app_name: str) -> bool:
        if app_name and app_name.strip():
            if self.current_app:
                self.previous_app = self.current_app
                
            self.current_app = app_name.strip().lower()
            self.context_start_time = time.time()
            
            self.app_history.append({
                'app': self.current_app,
                'timestamp': self.context_start_time
            })
            
            if len(self.app_history) > 50:
                self.app_history.pop(0)
            
            if self.current_app not in self.app_states:
                self.app_states[self.current_app] = {}
            
            print(f"🎯 Context switched to: {self.current_app}")
            return True
        return False
    
    def get_current_context(self) -> Optional[str]:
        return self.current_app
    
    def get_previous_context(self) -> Optional[str]:
        return self.previous_app
    
    def clear_context(self) -> None:
        self.previous_app = self.current_app
        self.current_app = None
        self.context_start_time = None
        print("🎯 Context cleared")
    
    def switch_to_previous(self) -> Optional[str]:
        if self.previous_app:
            temp = self.current_app
            self.current_app = self.previous_app
            self.previous_app = temp
            self.context_start_time = time.time()
            print(f"🎯 Switched back to: {self.current_app}")
            return self.current_app
        return None
    
    def is_in_app_context(self) -> bool:
        return self.current_app is not None
    
    def get_context_duration(self) -> Optional[float]:
        if self.context_start_time:
            return time.time() - self.context_start_time
        return None
    
    def get_app_state(self, key: str) -> Any:
        if self.current_app and self.current_app in self.app_states:
            return self.app_states[self.current_app].get(key)
        return None
    
    def set_app_state(self, key: str, value: Any) -> bool:
        if self.current_app:
            if self.current_app not in self.app_states:
                self.app_states[self.current_app] = {}
            self.app_states[self.current_app][key] = value
            return True
        return False
    
    def get_recent_apps(self, count: int = 5) -> list:
        recent = []
        seen = set()
        
        for entry in reversed(self.app_history):
            app = entry['app']
            if app not in seen:
                recent.append(app)
                seen.add(app)
            if len(recent) >= count:
                break
        
        return recent
    
    def get_context_info(self) -> Dict[str, Any]:
        return {
            'current_app': self.current_app,
            'previous_app': self.previous_app,
            'duration': self.get_context_duration(),
            'in_context': self.is_in_app_context(),
            'recent_apps': self.get_recent_apps(5)
        }

