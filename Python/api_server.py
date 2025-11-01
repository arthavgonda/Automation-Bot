
import sys
import os
import json
import asyncio
import threading
import queue
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(str(Path(__file__).parent))

from STT.RTMicroPhone import stream_microPhone, SpeechDetector
from STT.sttOffline import stt_vosk
from STT.NetworkStatus import check_server_connectivity
from Browser.DriverManager import setup_driver
from Browser.IntelligentBrowser import process_voice_command, EnhancedIntelligentBrowser
from System.SystemController import SystemController
from SmartAssistant import SmartAssistant, process_voice_command_smart

try:
    from STT.sttWhisper import stt_whisper
    WHISPER_AVAILABLE = True
except ImportError:
    logger.warning("Whisper STT not available - using Vosk only")
    WHISPER_AVAILABLE = False
    stt_whisper = None

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from contextlib import asynccontextmanager
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "websockets"], check=True)
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from contextlib import asynccontextmanager

browser_driver = None
system_controller = None
voice_queue = queue.Queue()
websocket_connections = set()
is_listening = False
speech_detector = None

class VoiceCommand(BaseModel):
    command: str

class SystemStatus(BaseModel):
    status: str
    message: str
    timestamp: float

class CommandResponse(BaseModel):
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()

def _clean_response_message(message):
    if not message:
        return ""
    
    message_lower = message.lower()
    
    skip_indicators = [
        "action:", "executed:", "step", "looking for", "mapped to",
        "context switched", "context set", "opened:", "opening",
        "file created:", "folder created:", "cleaned:", "detected",
        "parsing", "attempting", "command processed"
    ]
    
    if any(indicator in message_lower for indicator in skip_indicators):
        return ""
    
    clean_message = message
    
    if " | " in clean_message:
        parts = clean_message.split(" | ")
        clean_message = parts[-1].strip()
    
    if clean_message.startswith("Created file:"):
        filename = clean_message.replace("Created file: ", "").strip()
        return f"Created {filename}"
    
    if clean_message.startswith("Opened "):
        return clean_message
    
    if clean_message.startswith("Switched to "):
        return clean_message
    
    if clean_message.startswith("Created folder:"):
        foldername = clean_message.replace("Created folder: ", "").strip()
        return f"Created folder {foldername}"
    
    if clean_message.startswith("Moved file to "):
        return clean_message
    
    if clean_message.startswith("Copied file to "):
        return clean_message
    
    if clean_message.startswith("Searched for:"):
        query = clean_message.replace("Searched for: ", "").strip()
        return f"Searched for {query}"
    
    return clean_message

def ensure_browser_driver():
    global browser_driver
    try:
        if browser_driver is None:
            browser_driver = setup_driver()
            if browser_driver:
                logger.info("Browser driver initialized on demand")
                return True
            return False
        
        try:
            browser_driver.current_url
            return True
        except:
            logger.info("Browser window closed, reopening...")
            try:
                browser_driver.quit()
            except:
                pass
            browser_driver = None
            browser_driver = setup_driver()
            if browser_driver:
                logger.info("Browser driver reopened successfully")
                return True
            return False
    except Exception as e:
        logger.error(f"Error ensuring browser driver: {e}")
        browser_driver = None
        return False

def initialize_system():
    global system_controller, browser_driver, speech_detector
    logger.info("Initializing system components...")
    system_controller = SystemController()
    logger.info("System controller initialized")
    speech_detector = SpeechDetector()
    logger.info("Speech detector initialized")
    browser_driver = None
    logger.info("Browser driver: Lazy loading enabled (will open on demand)")
    if WHISPER_AVAILABLE:
        network_available = check_server_connectivity("8.8.8.8", 53, 3)
        if network_available:
            logger.info("Network available - Whisper STT enabled")
        else:
            logger.info("Network unavailable - Vosk STT enabled")
    else:
        logger.info("Whisper not available - Using Vosk STT only")
    system_controller.get_system_info()
    logger.info("System initialization complete")

def process_voice_input(audio_np):
    global browser_driver, system_controller, speech_detector
    try:
        network_available = check_server_connectivity("8.8.8.8", 53, 3) if WHISPER_AVAILABLE else False
        if network_available and WHISPER_AVAILABLE:
            transcription = stt_whisper(audio_np)
        else:
            transcription = stt_vosk(audio_np)
        if transcription and transcription.strip():
            logger.info(f"Voice input: {transcription}")
            asyncio.create_task(manager.broadcast(json.dumps({
                "type": "voice_transcription",
                "text": transcription,
                "timestamp": time.time()
            })))
            needs_browser = any(keyword in transcription.lower() for keyword in 
                              ['search', 'browser', 'web', 'google', 'youtube', 'website', 'download', 'open website'])
            
            if needs_browser:
                if not ensure_browser_driver():
                    logger.warning("Browser not available for web command")
            
            if browser_driver and system_controller:
                try:
                    result = process_voice_command_smart(browser_driver, system_controller, transcription)
                    if result == "EXIT":
                        browser_driver = None
                except Exception as e:
                    if "closed window" in str(e).lower() or "window_handles" in str(e).lower():
                        logger.info("Browser closed, attempting to reopen...")
                        if ensure_browser_driver():
                            result = process_voice_command_smart(browser_driver, system_controller, transcription)
                        else:
                            class DummyDriver:
                                def get(self, url): pass
                                def quit(self): pass
                            dummy = DummyDriver()
                            assistant = SmartAssistant(dummy, system_controller)
                            assistant.process_command(transcription)
                    else:
                        raise
            elif system_controller:
                class DummyDriver:
                    def get(self, url): pass
                    def quit(self): pass
                dummy = DummyDriver()
                assistant = SmartAssistant(dummy, system_controller)
                assistant.process_command(transcription)
            if browser_driver and system_controller:
                try:
                    success, message = process_voice_command_smart(browser_driver, system_controller, transcription)
                    if success and message and message not in ["Command processed", "CONTINUE", "EXIT"]:
                        clean_message = _clean_response_message(message)
                        if clean_message:
                            asyncio.create_task(manager.broadcast(json.dumps({
                                "type": "command_result",
                                "text": transcription,
                                "result": clean_message,
                                "timestamp": time.time()
                            })))
                except Exception as e:
                    if "closed window" in str(e).lower() or "window_handles" in str(e).lower():
                        try:
                            if ensure_browser_driver():
                                success, message = process_voice_command_smart(browser_driver, system_controller, transcription)
                                if success and message and message not in ["Command processed", "CONTINUE", "EXIT"]:
                                    clean_message = _clean_response_message(message)
                                    if clean_message:
                                        asyncio.create_task(manager.broadcast(json.dumps({
                                            "type": "command_result",
                                            "text": transcription,
                                            "result": clean_message,
                                            "timestamp": time.time()
                                        })))
                        except:
                            pass
            elif system_controller:
                dummy = type('DummyDriver', (), {'get': lambda self, url: None, 'quit': lambda self: None})()
                assistant = SmartAssistant(dummy, system_controller)
                success, message = assistant.process_command(transcription)
                if success and message and message not in ["Command processed", "CONTINUE", "EXIT"]:
                    clean_message = _clean_response_message(message)
                    if clean_message:
                        asyncio.create_task(manager.broadcast(json.dumps({
                            "type": "command_result",
                            "text": transcription,
                            "result": clean_message,
                            "timestamp": time.time()
                        })))
        return transcription
    except Exception as e:
        logger.error(f"Error processing voice input: {e}")
        asyncio.create_task(manager.broadcast(json.dumps({
            "type": "error",
            "message": str(e),
            "timestamp": time.time()
        })))
        return None

def start_voice_listening():
    global is_listening
    if is_listening:
        return
    is_listening = True
    logger.info("Starting voice recognition...")
    def voice_thread():
        try:
            stream_microPhone(process_voice_input, buffer_seconds=3)
        except Exception as e:
            logger.error(f"Voice recognition error: {e}")
        finally:
            is_listening = False
    thread = threading.Thread(target=voice_thread, daemon=True)
    thread.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_system()
    yield
    if browser_driver:
        try:
            browser_driver.quit()
        except:
            pass

app = FastAPI(
    title="EitherAssistant API",
    description="Voice-controlled system automation API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "EitherAssistant API Server", "status": "running"}

@app.get("/status")
async def get_status():
    return {
        "status": "online",
        "voice_listening": is_listening,
        "browser_enabled": browser_driver is not None,
        "system_controller": system_controller is not None,
        "timestamp": time.time()
    }

@app.post("/voice/start")
async def start_voice():
    global is_listening
    if not is_listening:
        start_voice_listening()
        return {"success": True, "message": "Voice recognition started"}
    else:
        return {"success": True, "message": "Voice recognition already running"}

@app.post("/voice/stop")
async def stop_voice():
    global is_listening
    is_listening = False
    return {"success": True, "message": "Voice recognition stopped"}

@app.post("/command")
async def process_command(command: VoiceCommand):
    global browser_driver, system_controller
    try:
        if system_controller:
            needs_browser = any(keyword in command.command.lower() for keyword in 
                              ['search', 'browser', 'web', 'google', 'youtube', 'website', 'download', 'open website'])
            
            if needs_browser:
                if not ensure_browser_driver():
                    return CommandResponse(
                        success=False,
                        message="Failed to initialize browser. Please check browser installation."
                    )
            
            if browser_driver:
                try:
                    success, message = process_voice_command_smart(browser_driver, system_controller, command.command)
                    result_message = _clean_response_message(message) if success else f"Error: {message}"
                except Exception as e:
                    if "closed window" in str(e).lower() or "window_handles" in str(e).lower():
                        logger.info("Browser closed, attempting to reopen...")
                        if ensure_browser_driver():
                            success, message = process_voice_command_smart(browser_driver, system_controller, command.command)
                            result_message = _clean_response_message(message) if success else f"Error: {message}"
                        else:
                            class DummyDriver:
                                def get(self, url): pass
                                def quit(self): pass
                            dummy = DummyDriver()
                            assistant = SmartAssistant(dummy, system_controller)
                            success, message = assistant.process_command(command.command)
                            result_message = _clean_response_message(message) if success else f"Error: {message}"
                    else:
                        result_message = f"Error: {str(e)}"
                        success = False
            else:
                class DummyDriver:
                    def get(self, url): pass
                    def quit(self): pass
                dummy = DummyDriver()
                assistant = SmartAssistant(dummy, system_controller)
                success, message = assistant.process_command(command.command)
                result_message = _clean_response_message(message) if success else f"Error: {message}"
            
            return CommandResponse(
                success=success,
                message=result_message,
                result={"output": result_message}
            )
        else:
            return CommandResponse(
                success=False,
                message="System controller not initialized"
            )
    except Exception as e:
        logger.error(f"Error processing command: {e}")
        return CommandResponse(
            success=False,
            message=f"Error: {str(e)}"
        )

@app.post("/browser/enable")
async def enable_browser():
    global browser_driver
    try:
        if not browser_driver:
            browser_driver = setup_driver()
            if browser_driver:
                return {"success": True, "message": "Browser automation enabled"}
            else:
                return {"success": False, "message": "Failed to initialize browser"}
        else:
            return {"success": True, "message": "Browser already enabled"}
    except Exception as e:
        logger.error(f"Error enabling browser: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/browser/disable")
async def disable_browser():
    global browser_driver
    try:
        if browser_driver:
            browser_driver.quit()
            browser_driver = None
            return {"success": True, "message": "Browser automation disabled"}
        else:
            return {"success": True, "message": "Browser already disabled"}
    except Exception as e:
        logger.error(f"Error disabling browser: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/system/info")
async def get_system_info():
    if system_controller:
        return {
            "success": True,
            "info": system_controller.get_system_info()
        }
    else:
        return {"success": False, "message": "System controller not initialized"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Not running in a virtual environment")
        print("Consider running: python -m venv venv && source venv/bin/activate")
    print("Starting EitherAssistant API Server...")
    print("API will be available at: http://localhost:8000")
    print("WebSocket endpoint: ws://localhost:8000/ws")
    print("API documentation: http://localhost:8000/docs")
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )